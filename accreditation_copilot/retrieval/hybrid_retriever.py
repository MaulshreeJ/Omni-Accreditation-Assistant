"""
Hybrid Retriever - Phase 2
Combines FAISS and BM25 retrieval with score fusion.

Performance Fix: Uses ModelManager for shared model instances.
"""

import re
import numpy as np
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from retrieval.index_loader import IndexLoader
from retrieval.score_fusion import ScoreFusion
from models.model_manager import get_model_manager


class HybridRetriever:
    """
    Hybrid retrieval combining dense (FAISS) and sparse (BM25) search.
    Uses shared models from ModelManager for performance.
    """
    
    # Index mapping
    INDEX_MAP = {
        ('NAAC', 'metric'): 'naac_metric',
        ('NAAC', 'policy'): 'naac_policy',
        ('NBA', 'metric'): 'nba_metric',
        ('NBA', 'policy'): 'nba_policy',
        ('NBA', 'prequalifier'): 'nba_prequalifier'
    }
    
    def __init__(self, model_manager=None):
        """
        Initialize hybrid retriever with shared models.
        
        Args:
            model_manager: Optional ModelManager instance (for testing)
        """
        self.index_loader = IndexLoader()
        self.score_fusion = ScoreFusion()
        
        # Get shared embedder from ModelManager
        if model_manager is None:
            model_manager = get_model_manager()
        self.model = model_manager.get_embedder()
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _reciprocal_rank_fusion(self, bm25_results: List[Dict], 
                                embedding_results: List[Dict], 
                                k: int = 60) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF) for combining BM25 and embedding results.
        
        RRF formula: score(d) = sum(1 / (k + rank(d)))
        
        Args:
            bm25_results: Results from BM25 search
            embedding_results: Results from embedding search
            k: Constant to prevent division by zero (default: 60)
            
        Returns:
            Fused results sorted by RRF score
        """
        scores = {}
        
        # BM25 contribution
        for rank, doc in enumerate(bm25_results, start=1):
            doc_id = doc["chunk_id"]
            if doc_id not in scores:
                scores[doc_id] = {
                    "doc": doc,
                    "rrf_score": 0.0,
                    "bm25_rank": None,
                    "embedding_rank": None
                }
            scores[doc_id]["rrf_score"] += 1.0 / (k + rank)
            scores[doc_id]["bm25_rank"] = rank
        
        # Embedding contribution
        for rank, doc in enumerate(embedding_results, start=1):
            doc_id = doc["chunk_id"]
            if doc_id not in scores:
                scores[doc_id] = {
                    "doc": doc,
                    "rrf_score": 0.0,
                    "bm25_rank": None,
                    "embedding_rank": None
                }
            scores[doc_id]["rrf_score"] += 1.0 / (k + rank)
            scores[doc_id]["embedding_rank"] = rank
            
            # If doc wasn't in BM25 results, copy its metadata
            if scores[doc_id]["bm25_rank"] is None:
                scores[doc_id]["doc"] = doc
        
        # Sort by RRF score
        fused = sorted(
            scores.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )
        
        # Extract documents with RRF scores
        results = []
        for item in fused:
            doc = item["doc"].copy()
            doc["rrf_score"] = item["rrf_score"]
            doc["fused_score"] = item["rrf_score"]  # For backward compatibility
            results.append(doc)
        
        return results
    
    def retrieve(self, variants: List[str], framework: str, query_type: str,
                original_query: str, explicit_metric: str = None, 
                top_k_per_variant: int = 10, final_top_k: int = 30) -> List[Dict]:
        """
        Multi-query hybrid retrieval with RRF fusion across query variants.
        
        This implementation performs independent retrieval for each query variant
        and fuses all results using RRF, which significantly improves recall.
        
        Args:
            variants: List of query variants
            framework: NAAC or NBA
            query_type: metric, policy, or prequalifier
            original_query: Original user query (for criterion boost)
            explicit_metric: Pre-extracted explicit metric ID
            top_k_per_variant: Results per variant (default: 10)
            final_top_k: Final number of results to return
            
        Returns:
            Top-K results with fused scores
        """
        # Get index name
        index_key = (framework, query_type)
        if index_key not in self.INDEX_MAP:
            raise ValueError(f"Invalid index key: {index_key}")
        
        index_name = self.INDEX_MAP[index_key]
        
        # Limit to 3 query variants for efficiency (include original query)
        query_variants = [original_query] + variants[:2]
        
        # STEP 1: Collect all BM25 and embedding results from all query variants
        all_bm25_results = []
        all_embedding_results = []
        
        for variant in query_variants:
            # Embed variant
            embedding = self.model.encode(variant, convert_to_numpy=True)
            
            # Tokenize variant
            tokens = self._tokenize(variant)
            
            # FAISS search
            dense_results = self.index_loader.search_faiss(
                index_name, embedding, top_k=top_k_per_variant
            )
            
            # BM25 search
            bm25_results = self.index_loader.search_bm25(
                index_name, tokens, top_k=top_k_per_variant
            )
            
            # Collect results from this variant
            all_bm25_results.extend(bm25_results)
            all_embedding_results.extend(dense_results)
        
        # STEP 2: Apply RRF fusion across all collected results
        # This fuses results from all query variants together
        fused_results = self._reciprocal_rank_fusion(all_bm25_results, all_embedding_results, k=60)
        
        # STEP 3: Limit candidates before further processing
        results = fused_results[:final_top_k]
        
        # PART 2: Multiplicative criterion boost
        if explicit_metric:
            # Collect chunk IDs that need metadata
            chunk_ids_to_check = [r['chunk_id'] for r in results]
            
            # Fetch metadata for all chunks (do this in main thread, not executor)
            # We'll apply boost based on chunk_id pattern matching instead
            for result in results:
                chunk_id = result['chunk_id']
                
                # Extract criterion from chunk_id if possible
                # Format: framework_source_criterion_page_order
                # Example: NAAC_NAAC_SSR_Manual_Universities.pdf_3.2.1_65_0
                parts = chunk_id.split('_')
                
                # Try to find criterion in chunk_id
                chunk_criterion = None
                for part in parts:
                    # Check if part matches criterion pattern
                    if '.' in part and part.replace('.', '').isdigit():
                        chunk_criterion = part
                        break
                    elif part.startswith('C') and part[1:].isdigit():
                        chunk_criterion = part
                        break
                    elif part.startswith('PO') or part.startswith('PEO'):
                        chunk_criterion = part
                        break
                
                if chunk_criterion:
                    # Extract prefix (e.g., "3.2" from "3.2.1")
                    if '.' in explicit_metric:
                        prefix = ".".join(explicit_metric.split(".")[:2])
                    else:
                        prefix = explicit_metric
                    
                    # Exact match: 1.25x boost
                    if chunk_criterion == explicit_metric:
                        result['fused_score'] *= 1.25
                    # Sibling criterion: 1.10x boost
                    elif chunk_criterion.startswith(prefix):
                        result['fused_score'] *= 1.10
        
        # Sort by fused score
        results.sort(key=lambda x: x['fused_score'], reverse=True)
        
        # FIX 2: Ensure we always return a list, never None
        final_results = results[:final_top_k]
        return final_results if final_results else []
    
    def close(self):
        """Close resources."""
        self.index_loader.close()


# Test function
if __name__ == "__main__":
    retriever = HybridRetriever()
    
    variants = [
        "Are we compliant with NAAC 3.2.1?",
        "Does our institution meet NAAC metric 3.2.1 requirements?",
        "What is needed for NAAC 3.2.1 compliance?"
    ]
    
    results = retriever.retrieve(
        variants=variants,
        framework='NAAC',
        query_type='metric',
        original_query="Are we compliant with NAAC 3.2.1?",
        final_top_k=10
    )
    
    print(f"Retrieved {len(results)} results")
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. Chunk ID: {result['chunk_id']}")
        print(f"   Dense: {result['dense_score']:.3f}, BM25: {result['bm25_score']:.3f}, Fused: {result['fused_score']:.3f}")
    
    retriever.close()
