"""
Evidence Strength Scorer - Phase 6 Capability 3
Scores evidence as Strong/Moderate/Weak based on multiple factors.
"""

from typing import List, Dict, Any


class EvidenceStrengthScorer:
    """Score evidence strength for compliance evaluation."""
    
    def score_evidence_strength(
        self,
        retrieval_results: List[Dict[str, Any]],
        per_chunk_hits: Dict[str, List[str]],
        evidence_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score evidence strength across all chunks.
        
        Args:
            retrieval_results: Retrieved evidence chunks
            per_chunk_hits: Mapping of chunk_id -> dimensions covered
            evidence_scores: Evidence quality scores from Phase 3
            
        Returns:
            Evidence strength analysis
        """
        # Filter to institution chunks only
        institution_chunks = [
            r for r in retrieval_results 
            if r.get('source_type') == 'institution'
        ]
        
        if not institution_chunks:
            return {
                'overall_strength': 'None',
                'strong_count': 0,
                'moderate_count': 0,
                'weak_count': 0,
                'per_chunk_strength': {}
            }
        
        # Score each chunk
        per_chunk_strength = {}
        strong_count = 0
        moderate_count = 0
        weak_count = 0
        
        for result in institution_chunks:
            chunk_id = result.get('chunk_id', '')
            
            # Calculate strength score
            strength_score, strength_label = self._calculate_chunk_strength(
                result,
                per_chunk_hits.get(chunk_id, []),
                evidence_scores
            )
            
            per_chunk_strength[chunk_id] = {
                'strength': strength_label,
                'score': strength_score,
                'dimensions_covered': len(per_chunk_hits.get(chunk_id, []))
            }
            
            # Count by strength
            if strength_label == 'Strong':
                strong_count += 1
            elif strength_label == 'Moderate':
                moderate_count += 1
            else:
                weak_count += 1
        
        # Determine overall strength
        overall_strength = self._determine_overall_strength(
            strong_count,
            moderate_count,
            weak_count
        )
        
        return {
            'overall_strength': overall_strength,
            'strong_count': strong_count,
            'moderate_count': moderate_count,
            'weak_count': weak_count,
            'per_chunk_strength': per_chunk_strength
        }
    
    def _calculate_chunk_strength(
        self,
        result: Dict[str, Any],
        dimensions_covered: List[str],
        evidence_scores: Dict[str, Any]
    ) -> tuple:
        """
        Calculate strength for a single chunk.
        
        Factors:
        1. Number of dimensions covered (breadth)
        2. Reranker score (relevance)
        3. Final score (weighted relevance)
        
        Args:
            result: Retrieval result
            dimensions_covered: Dimensions this chunk covers
            evidence_scores: Evidence quality scores
            
        Returns:
            (strength_score, strength_label)
        """
        # Factor 1: Dimension coverage (0-1)
        # More dimensions = stronger evidence
        dimension_score = min(len(dimensions_covered) / 3.0, 1.0)
        
        # Factor 2: Reranker score (already 0-1)
        reranker_score = result.get('reranker_score', 0.0)
        
        # Factor 3: Final score (weighted, normalize to 0-1)
        final_score = result.get('final_score', 0.0)
        # Final scores can be > 1 due to evidence weight, normalize
        final_score_normalized = min(final_score / 3.0, 1.0)
        
        # Combined strength score (weighted average)
        strength_score = (
            0.4 * dimension_score +
            0.3 * reranker_score +
            0.3 * final_score_normalized
        )
        
        # Classify strength
        if strength_score >= 0.7:
            strength_label = 'Strong'
        elif strength_score >= 0.4:
            strength_label = 'Moderate'
        else:
            strength_label = 'Weak'
        
        return strength_score, strength_label
    
    def _determine_overall_strength(
        self,
        strong_count: int,
        moderate_count: int,
        weak_count: int
    ) -> str:
        """
        Determine overall evidence strength.
        
        Args:
            strong_count: Number of strong chunks
            moderate_count: Number of moderate chunks
            weak_count: Number of weak chunks
            
        Returns:
            Overall strength label
        """
        total = strong_count + moderate_count + weak_count
        
        if total == 0:
            return 'None'
        
        # Calculate percentages
        strong_pct = strong_count / total
        moderate_pct = moderate_count / total
        
        # Classification rules
        if strong_pct >= 0.5:
            return 'Strong'
        elif strong_pct + moderate_pct >= 0.7:
            return 'Moderate'
        else:
            return 'Weak'
