"""
Score Fusion - Phase 2
Normalizes and fuses dense and sparse scores.
"""

import numpy as np
from typing import List, Dict


class ScoreFusion:
    """
    Normalizes and fuses FAISS and BM25 scores.
    """
    
    @staticmethod
    def normalize_dense(scores: List[float]) -> List[float]:
        """
        Normalize dense scores (already cosine similarity 0-1).
        
        Args:
            scores: List of dense scores
            
        Returns:
            Normalized scores
        """
        if not scores:
            return []
        
        scores = np.array(scores)
        
        # Clip to [0, 1] range (should already be there)
        scores = np.clip(scores, 0, 1)
        
        return scores.tolist()
    
    @staticmethod
    def normalize_bm25(scores: List[float]) -> List[float]:
        """
        Min-max normalize BM25 scores.
        
        Args:
            scores: List of BM25 scores
            
        Returns:
            Normalized scores [0, 1]
        """
        if not scores:
            return []
        
        scores = np.array(scores)
        
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score == min_score:
            # All scores are the same - return zeros to avoid BM25 dominance
            return [0.0 for _ in scores]
        
        # Min-max normalization
        normalized = (scores - min_score) / (max_score - min_score)
        
        return normalized.tolist()
    
    @staticmethod
    def fuse_scores(dense_scores: List[float], bm25_scores: List[float], 
                   weight_dense: float = 0.7) -> List[float]:
        """
        Fuse dense and BM25 scores with weighted average.
        
        Args:
            dense_scores: Normalized dense scores
            bm25_scores: Normalized BM25 scores
            weight_dense: Weight for dense scores (default 0.6)
            
        Returns:
            Fused scores
        """
        if not dense_scores or not bm25_scores:
            return []
        
        dense = np.array(dense_scores)
        bm25 = np.array(bm25_scores)
        
        weight_bm25 = 1.0 - weight_dense
        
        fused = (weight_dense * dense) + (weight_bm25 * bm25)
        
        return fused.tolist()
    
    @staticmethod
    def apply_criterion_boost(results: List[Dict], query: str, explicit_metric: str = None, 
                             boost: float = 0.25) -> List[Dict]:
        """
        Boost scores for chunks matching criterion in query.
        
        Args:
            results: List of result dicts with 'criterion' and 'fused_score'
            query: Original query
            explicit_metric: Pre-extracted metric ID (if any)
            boost: Boost amount (default 0.25 for explicit matches)
            
        Returns:
            Results with boosted scores
        """
        import re
        
        # Use explicit_metric if provided, otherwise extract from query
        target_criterion = explicit_metric
        
        if not target_criterion:
            # Extract NAAC metric pattern (e.g., 3.2.1)
            naac_match = re.search(r'\b(\d\.\d\.\d)\b', query)
            
            # Extract NBA PO/PEO pattern (e.g., PO1, PEO2)
            nba_match = re.search(r'\b(PO|PEO|PSO)(\d+)\b', query, re.IGNORECASE)
            
            if naac_match:
                target_criterion = naac_match.group(1)
            elif nba_match:
                target_criterion = f"{nba_match.group(1).upper()}{nba_match.group(2)}"
        
        if not target_criterion:
            return results
        
        # Apply stronger boost for explicit metric matches
        for result in results:
            chunk_criterion = result.get('criterion')
            if chunk_criterion and chunk_criterion == target_criterion:
                result['fused_score'] = min(1.0, result['fused_score'] + boost)
        
        return results


# Test function
if __name__ == "__main__":
    fusion = ScoreFusion()
    
    # Test normalization
    dense = [0.9, 0.8, 0.7, 0.6]
    bm25 = [15.2, 12.3, 10.1, 8.5]
    
    dense_norm = fusion.normalize_dense(dense)
    bm25_norm = fusion.normalize_bm25(bm25)
    
    print(f"Dense normalized: {dense_norm}")
    print(f"BM25 normalized: {bm25_norm}")
    
    # Test fusion
    fused = fusion.fuse_scores(dense_norm, bm25_norm, weight_dense=0.6)
    print(f"Fused scores: {fused}")
