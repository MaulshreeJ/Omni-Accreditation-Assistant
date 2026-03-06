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
    
    def retrieve(self, variants: List[str], framework: str, query_type: str,
                original_query: str, explicit_metric: str = None, 
                top_k_per_variant: int = 15, final_top_k: int = 20) -> List[Dict]:
        """
        Hybrid retrieval across query variants.
        
        Args:
            variants: List of query variants
            framework: NAAC or NBA
            query_type: metric, policy, or prequalifier
            original_query: Original user query (for criterion boost)
            explicit_metric: Pre-extracted explicit metric ID
            top_k_per_variant: Results per variant
            final_top_k: Final number of results to return
            
        Returns:
            Top-K results with fused scores
        """
        # Get index name
        index_key = (framework, query_type)
        if index_key not in self.INDEX_MAP:
            raise ValueError(f"Invalid index key: {index_key}")
        
        index_name = self.INDEX_MAP[index_key]
        
        # PART 1: Adaptive fusion weights based on explicit metric detection
        if explicit_metric:
            dense_weight = 0.85
            bm25_weight = 0.15
        else:
            dense_weight = 0.70
            bm25_weight = 0.30
        
        # Aggregate results across variants
        all_results = {}  # chunk_id -> best result
        
        for variant in variants:
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
            
            # Create lookup dicts
            dense_dict = {r['chunk_id']: r['dense_score'] for r in dense_results}
            bm25_dict = {r['chunk_id']: r['bm25_score'] for r in bm25_results}
            
            # Get all unique chunk IDs
            all_chunk_ids = set(dense_dict.keys()) | set(bm25_dict.keys())
            
            # Collect scores for normalization
            dense_scores = [dense_dict.get(cid, 0.0) for cid in all_chunk_ids]
            bm25_scores = [bm25_dict.get(cid, 0.0) for cid in all_chunk_ids]
            
            # Normalize
            dense_norm = self.score_fusion.normalize_dense(dense_scores)
            bm25_norm = self.score_fusion.normalize_bm25(bm25_scores)
            
            # Fuse with adaptive weights
            fused_scores = self.score_fusion.fuse_scores(
                dense_norm, bm25_norm, weight_dense=dense_weight
            )
            
            # Store results
            for i, chunk_id in enumerate(all_chunk_ids):
                result = {
                    'chunk_id': chunk_id,
                    'dense_score': dense_dict.get(chunk_id, 0.0),
                    'bm25_score': bm25_dict.get(chunk_id, 0.0),
                    'fused_score': fused_scores[i]
                }
                
                # Keep highest fused score per chunk
                if chunk_id not in all_results or result['fused_score'] > all_results[chunk_id]['fused_score']:
                    all_results[chunk_id] = result
        
        # Convert to list
        results = list(all_results.values())
        
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
        
        # Return top-K
        return results[:final_top_k]
    
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
