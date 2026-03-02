"""
Retrieval Pipeline - Phase 2
Async orchestration of hybrid retrieval with HyDE.
"""

import asyncio
import numpy as np
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.framework_router import FrameworkRouter
from retrieval.query_expander import QueryExpander
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.hyde_retriever import HyDERetriever
from retrieval.reranker import Reranker
from retrieval.index_loader import IndexLoader
from retrieval.parent_expander import ParentExpander


class RetrievalPipeline:
    """
    Async orchestration of full retrieval pipeline.
    """
    
    def __init__(self):
        self.router = FrameworkRouter()
        self.expander = QueryExpander()
        self.hybrid_retriever = HybridRetriever()
        self.hyde_retriever = HyDERetriever()
        self.reranker = Reranker()
        self.index_loader = IndexLoader()
        self.parent_expander = ParentExpander()
    
    def _extract_explicit_metric(self, query: str) -> tuple:
        """
        Extract explicit metric ID from query.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (metric_id, metric_type) or (None, None)
        """
        import re
        
        # NAAC metric pattern (e.g., 3.2.1)
        naac_match = re.search(r'\b(\d\.\d\.\d)\b', query)
        if naac_match:
            return naac_match.group(1), 'NAAC'
        
        # NBA PO pattern (e.g., PO1, PO12)
        po_match = re.search(r'\b(PO)(\d+)\b', query, re.IGNORECASE)
        if po_match:
            return f"{po_match.group(1).upper()}{po_match.group(2)}", 'NBA'
        
        # NBA PEO pattern (e.g., PEO1, PEO5)
        peo_match = re.search(r'\b(PEO)(\d+)\b', query, re.IGNORECASE)
        if peo_match:
            return f"{peo_match.group(1).upper()}{peo_match.group(2)}", 'NBA'
        
        # NBA Criterion pattern (e.g., Criterion 8)
        criterion_match = re.search(r'\bCriterion\s+(\d+)\b', query, re.IGNORECASE)
        if criterion_match:
            return f"C{criterion_match.group(1)}", 'NBA'
        
        return None, None
    
    def _fetch_exact_match_chunks(self, framework: str, criterion: str) -> List[str]:
        """
        Fetch chunk IDs that exactly match the criterion.
        
        Args:
            framework: NAAC or NBA
            criterion: Metric ID (e.g., "3.2.1", "PO1")
            
        Returns:
            List of chunk IDs
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect('data/metadata.db')
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT chunk_id FROM chunks WHERE framework = ? AND criterion = ?',
                (framework, criterion)
            )
            
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            print(f"Error fetching exact matches: {e}")
            return []
    
    async def _run_hybrid_retrieval(self, variants: List[str], framework: str, 
                                    query_type: str, original_query: str,
                                    explicit_metric: str = None) -> List[Dict]:
        """Run hybrid retrieval in async context."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.hybrid_retriever.retrieve,
            variants,
            framework,
            query_type,
            original_query,
            explicit_metric,  # Pass explicit metric
            15,  # top_k_per_variant
            20   # final_top_k
        )
    
    async def _run_hyde_retrieval(self, query: str, framework: str, 
                                  query_type: str) -> List[Dict]:
        """Run HyDE retrieval in async context."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.hyde_retriever.retrieve,
            query,
            framework,
            query_type,
            10  # top_k
        )
    
    def _should_use_hyde(self, hybrid_results: List[Dict], hyde_results: List[Dict]) -> bool:
        """
        Decide whether to merge HyDE results based on score comparison.
        Requires 5% improvement to merge.
        
        Args:
            hybrid_results: Results from hybrid retrieval
            hyde_results: Results from HyDE retrieval
            
        Returns:
            True if HyDE should be merged
        """
        if not hyde_results:
            return False
        
        if not hybrid_results:
            return True
        
        # Calculate average scores (top 10)
        avg_hybrid = np.mean([r['fused_score'] for r in hybrid_results[:10]])
        avg_hyde = np.mean([r['dense_score'] for r in hyde_results[:10]])
        
        # Require 5% improvement
        return avg_hyde > avg_hybrid * 1.05
    
    def _merge_results(self, hybrid_results: List[Dict], hyde_results: List[Dict]) -> List[Dict]:
        """
        Merge hybrid and HyDE results.
        
        Args:
            hybrid_results: Results from hybrid retrieval
            hyde_results: Results from HyDE retrieval
            
        Returns:
            Merged results (top 20)
        """
        # Create lookup dict
        merged = {}
        
        # Add hybrid results
        for result in hybrid_results:
            merged[result['chunk_id']] = result
        
        # Add HyDE results (if not already present or if score is higher)
        for result in hyde_results:
            chunk_id = result['chunk_id']
            
            # Use dense_score as fused_score for HyDE results
            if 'fused_score' not in result:
                result['fused_score'] = result['dense_score']
                result['bm25_score'] = 0.0  # HyDE doesn't use BM25
            
            if chunk_id not in merged or result['fused_score'] > merged[chunk_id]['fused_score']:
                merged[chunk_id] = result
        
        # Convert to list and sort
        results = list(merged.values())
        results.sort(key=lambda x: x['fused_score'], reverse=True)
        
        return results[:20]
    
    def _enrich_with_metadata(self, results: List[Dict]) -> List[Dict]:
        """
        Enrich results with full metadata from database.
        
        Args:
            results: Results with chunk_id and scores
            
        Returns:
            Enriched results with full metadata
        """
        enriched = []
        
        for result in results:
            chunk = self.index_loader.get_chunk_metadata(result['chunk_id'])
            
            if chunk:
                enriched_result = {
                    'chunk_id': result['chunk_id'],
                    'framework': chunk['framework'],
                    'doc_type': chunk['doc_type'],
                    'criterion': chunk.get('criterion'),
                    'source': chunk['source'],
                    'page': chunk['page'],
                    'text': chunk['text'],
                    'scores': {
                        'dense': result.get('dense_score', 0.0),
                        'bm25': result.get('bm25_score', 0.0),
                        'fused': result.get('fused_score', 0.0),
                        'reranker': result.get('reranker_score', 0.0)
                    }
                }
                enriched.append(enriched_result)
        
        return enriched
    
    def _ensure_exact_matches(self, candidates: List[Dict], exact_match_chunk_ids: List[str]) -> List[Dict]:
        """
        Ensure exact match chunks are included in candidates.
        
        Args:
            candidates: Current candidate list
            exact_match_chunk_ids: Chunk IDs that must be included
            
        Returns:
            Updated candidates with exact matches guaranteed
        """
        if not exact_match_chunk_ids:
            return candidates
        
        # Get existing chunk IDs
        existing_ids = set(c['chunk_id'] for c in candidates)
        
        # Add missing exact matches
        for chunk_id in exact_match_chunk_ids:
            if chunk_id not in existing_ids:
                # Add with high fused score to ensure inclusion
                candidates.append({
                    'chunk_id': chunk_id,
                    'dense_score': 0.9,
                    'bm25_score': 0.0,
                    'fused_score': 0.9  # High score to ensure inclusion
                })
        
        # Re-sort by fused score
        candidates.sort(key=lambda x: x['fused_score'], reverse=True)
        
        return candidates[:20]  # Keep top 20
    
    async def run_retrieval(self, query: str, verbose: bool = False, 
                           enable_parent_expansion: bool = True) -> List[Dict]:
        """
        Run full retrieval pipeline.
        
        Args:
            query: User query
            verbose: Print debug information
            enable_parent_expansion: Enable parent context expansion (Phase 2.2)
            
        Returns:
            Top-5 reranked results with full metadata (and parent context if enabled)
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"RETRIEVAL PIPELINE")
            print(f"{'='*60}")
            print(f"Query: {query}\n")
        
        # Step 1: Extract explicit metric ID
        explicit_metric, metric_framework = self._extract_explicit_metric(query)
        
        if verbose and explicit_metric:
            print(f"Explicit Metric Detected: {explicit_metric} ({metric_framework})")
        
        # Step 2: Route framework
        routing = self.router.route_framework(query)
        framework = routing['framework']
        query_type = routing['query_type']
        
        if verbose:
            print(f"Routing: Framework={framework}, Type={query_type}")
        
        # Step 3: Fetch exact match chunks if explicit metric exists
        exact_match_chunk_ids = []
        if explicit_metric:
            exact_match_chunk_ids = self._fetch_exact_match_chunks(framework, explicit_metric)
            if verbose:
                print(f"Exact Match Chunks: {len(exact_match_chunk_ids)} found")
        
        # Step 4: Expand query
        variants = self.expander.expand_query(query, framework)
        
        if verbose:
            print(f"\nQuery Variants ({len(variants)}):")
            for i, variant in enumerate(variants, 1):
                print(f"  {i}. {variant}")
        
        # Step 5: Run hybrid and HyDE retrieval in parallel
        if verbose:
            print(f"\nRunning parallel retrieval...")
        
        hybrid_results, hyde_results = await asyncio.gather(
            self._run_hybrid_retrieval(variants, framework, query_type, query, explicit_metric),
            self._run_hyde_retrieval(query, framework, query_type)
        )
        
        if verbose:
            print(f"  Hybrid: {len(hybrid_results)} results")
            print(f"  HyDE: {len(hyde_results)} results")
        
        # Step 6: Conditional merge
        use_hyde = self._should_use_hyde(hybrid_results, hyde_results)
        
        if verbose:
            if use_hyde:
                avg_hybrid = np.mean([r['fused_score'] for r in hybrid_results[:10]]) if hybrid_results else 0
                avg_hyde = np.mean([r['dense_score'] for r in hyde_results[:10]]) if hyde_results else 0
                print(f"\nHyDE Decision: MERGE (HyDE avg={avg_hyde:.3f} > Hybrid avg={avg_hybrid:.3f} * 1.05)")
            else:
                print(f"\nHyDE Decision: SKIP (Hybrid stronger or insufficient improvement)")
        
        if use_hyde:
            candidates = self._merge_results(hybrid_results, hyde_results)
        else:
            candidates = hybrid_results[:20]
        
        # Step 7: Ensure exact matches are included
        if exact_match_chunk_ids:
            candidates = self._ensure_exact_matches(candidates, exact_match_chunk_ids)
            if verbose:
                print(f"Exact matches ensured in candidates")
        
        if verbose:
            print(f"Candidates for reranking: {len(candidates)}")
        
        # Step 8: Rerank
        if verbose:
            print(f"\nReranking...")
        
        top_5 = self.reranker.rerank(query, candidates, top_k=5)
        
        # Step 9: Enrich with metadata
        results = self._enrich_with_metadata(top_5)
        
        # Step 10: Parent expansion (Phase 2.2)
        if enable_parent_expansion:
            if verbose:
                print(f"\nExpanding with parent context...")
            
            results = self.parent_expander.expand_with_parent(results)
            
            if verbose:
                print(f"Parent expansion complete")
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"TOP-5 RESULTS")
            print(f"{'='*60}")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. [{result['framework']}] {result['source']} (Page {result['page']})")
                print(f"   Type: {result['doc_type']}, Criterion: {result.get('criterion', 'N/A')}")
                print(f"   Scores: Dense={result['scores']['dense']:.3f}, "
                      f"BM25={result['scores']['bm25']:.3f}, "
                      f"Fused={result['scores']['fused']:.3f}, "
                      f"Reranker={result['scores']['reranker']:.3f}")
                
                # Show parent expansion metadata if available
                if 'metadata' in result:
                    meta = result['metadata']
                    print(f"   Parent Section: {meta['parent_section_id']}")
                    print(f"   Siblings Used: {meta['num_siblings_used']}")
                    print(f"   Child Tokens: {meta['child_tokens']}, Parent Tokens: {meta['parent_tokens']}")
                
                # Handle Unicode characters in text
                try:
                    if 'child_text' in result:
                        text_preview = result['child_text'][:150].encode('ascii', 'ignore').decode('ascii')
                    else:
                        text_preview = result['text'][:150].encode('ascii', 'ignore').decode('ascii')
                    print(f"   Text: {text_preview}...")
                except:
                    text_len = len(result.get('child_text', result.get('text', '')))
                    print(f"   Text: [Unicode text - {text_len} chars]")
        
        return results
    
    def close(self):
        """Close all resources."""
        self.hybrid_retriever.close()
        self.hyde_retriever.close()
        self.reranker.close()
        self.index_loader.close()


# Test function
async def main():
    pipeline = RetrievalPipeline()
    
    test_queries = [
        "Are we compliant with NAAC 3.2.1?",
        "What are the minimum faculty requirements for NBA Tier-II?",
        "How long is NBA accreditation valid?"
    ]
    
    for query in test_queries:
        results = await pipeline.run_retrieval(query, verbose=True)
        print(f"\n{'='*60}\n")
    
    pipeline.close()


if __name__ == "__main__":
    asyncio.run(main())
