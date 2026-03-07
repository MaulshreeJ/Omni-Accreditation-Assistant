"""
C3 - Confidence Calculator
Combines evidence strength and retrieval quality to produce confidence score.

FIXED: Multiplicative penalty for missing dimensions.
"""

from typing import List, Dict, Any


class ConfidenceCalculator:
    """Calculate confidence score and compliance status."""
    
    # Status thresholds
    THRESHOLDS = {
        'high': 0.75,
        'partial': 0.50,
        'weak': 0.25
    }
    
    def calculate(
        self,
        evidence_scores: List[Dict[str, Any]],
        coverage: Dict[str, Any],
        retrieval_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate confidence score and status.
        
        FIXED: Multiplicative penalty for missing dimensions.
        
        Args:
            evidence_scores: Output from EvidenceScorer
            coverage: Output from DimensionChecker
            retrieval_results: Original Phase 2 results
            
        Returns:
            Confidence analysis with score and status
        """
        # Average evidence score
        avg_evidence_score = (
            sum(e['evidence_score'] for e in evidence_scores) / len(evidence_scores)
            if evidence_scores else 0.0
        )
        
        # Average retrieval score (reranker) - handle both formats
        total_reranker_score = 0.0
        for r in retrieval_results:
            score = r.get('reranker_score', 0.0)
            if score == 0.0:
                # Try nested format
                score = r.get('scores', {}).get('reranker', 0.0)
            total_reranker_score += score
        
        avg_retrieval_score = (
            total_reranker_score / len(retrieval_results)
            if retrieval_results else 0.0
        )
        
        # Base score: weighted combination
        base_score = (
            0.6 * avg_evidence_score +
            0.4 * avg_retrieval_score
        )
        
        # Coverage ratio (FIXED: multiplicative penalty)
        coverage_ratio = coverage.get('coverage_ratio', 0.0)
        
        # Final confidence: base score × coverage ratio
        # This ensures missing dimensions penalize the score
        confidence_score = base_score * coverage_ratio
        
        # Determine status
        status = self._determine_status(confidence_score)
        
        return {
            'confidence_score': round(confidence_score, 3),
            'status': status,
            'base_score': round(base_score, 3),
            'avg_evidence_score': round(avg_evidence_score, 3),
            'avg_retrieval_score': round(avg_retrieval_score, 3),
            'coverage_ratio': round(coverage_ratio, 3)
        }
    
    def _determine_status(self, confidence_score: float) -> str:
        """Map confidence score to status."""
        if confidence_score >= self.THRESHOLDS['high']:
            return 'High'
        elif confidence_score >= self.THRESHOLDS['partial']:
            return 'Partial'
        elif confidence_score >= self.THRESHOLDS['weak']:
            return 'Weak'
        else:
            return 'Insufficient'
