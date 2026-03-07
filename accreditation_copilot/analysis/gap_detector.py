"""
Gap Detector - Phase 6 Capability 2
Automatically identifies compliance gaps from coverage analysis.
"""

from typing import List, Dict, Any


class GapDetector:
    """Detect compliance gaps from dimension coverage."""
    
    def detect_gaps(
        self,
        coverage: Dict[str, Any],
        confidence: Dict[str, Any],
        institution_evidence_available: bool
    ) -> List[Dict[str, Any]]:
        """
        Identify compliance gaps.
        
        Args:
            coverage: Dimension coverage analysis
            confidence: Confidence scores
            institution_evidence_available: Whether institution evidence exists
            
        Returns:
            List of identified gaps with severity
        """
        gaps = []
        
        # Gap 1: Missing institution evidence
        if not institution_evidence_available:
            gaps.append({
                'gap_type': 'no_evidence',
                'severity': 'critical',
                'description': 'No institutional evidence available for this criterion',
                'recommendation': 'Upload institutional documents containing evidence for this criterion'
            })
            return gaps  # No point checking other gaps if no evidence
        
        # Gap 2: Missing required dimensions
        dimensions_missing = coverage.get('dimensions_missing', [])
        if dimensions_missing:
            gaps.append({
                'gap_type': 'missing_dimensions',
                'severity': 'high',
                'description': f'Missing coverage for required dimensions: {", ".join(dimensions_missing)}',
                'dimensions': dimensions_missing,
                'recommendation': 'Provide evidence addressing these specific dimensions'
            })
        
        # Gap 3: Low coverage ratio
        coverage_ratio = coverage.get('coverage_ratio', 0.0)
        if coverage_ratio < 0.5 and institution_evidence_available:
            gaps.append({
                'gap_type': 'low_coverage',
                'severity': 'high',
                'description': f'Low dimension coverage: {coverage_ratio:.1%}',
                'coverage_ratio': coverage_ratio,
                'recommendation': 'Expand evidence to cover more required dimensions'
            })
        
        # Gap 4: Low confidence
        overall_confidence = confidence.get('overall_confidence', 0.0)
        if overall_confidence < 0.5 and institution_evidence_available:
            gaps.append({
                'gap_type': 'low_confidence',
                'severity': 'medium',
                'description': f'Low confidence score: {overall_confidence:.1%}',
                'confidence_score': overall_confidence,
                'recommendation': 'Provide more detailed or higher-quality evidence'
            })
        
        # Gap 5: Weak evidence quality
        evidence_quality = confidence.get('evidence_quality', 0.0)
        if evidence_quality < 0.4 and institution_evidence_available:
            gaps.append({
                'gap_type': 'weak_evidence',
                'severity': 'medium',
                'description': f'Weak evidence quality: {evidence_quality:.1%}',
                'evidence_quality': evidence_quality,
                'recommendation': 'Improve evidence specificity and relevance'
            })
        
        return gaps
    
    def prioritize_gaps(self, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize gaps by severity.
        
        Args:
            gaps: List of detected gaps
            
        Returns:
            Sorted list (critical -> high -> medium -> low)
        """
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(gaps, key=lambda g: severity_order.get(g['severity'], 99))
