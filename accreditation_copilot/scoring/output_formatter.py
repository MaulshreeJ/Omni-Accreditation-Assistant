"""
C5 - Output Formatter
Assembles final compliance report in structured JSON format.

ENHANCED: Now includes Phase 5 evidence mapping and D5 audit enrichment.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.audit_enricher import AuditEnricher
from mapping.evidence_mapper import EvidenceMapper


class ComplianceReport(BaseModel):
    """Pydantic model for compliance report validation."""
    
    run_id: str
    timestamp: str
    query: str
    framework: str
    criterion: str
    metric_name: str
    
    confidence_score: float = Field(ge=0.0, le=1.0)
    compliance_status: str
    
    dimensions_covered: List[str]
    dimensions_missing: List[str]
    coverage_ratio: float = Field(ge=0.0, le=1.0)
    
    evidence_summary: str
    gaps: List[str]
    recommendation: str
    
    # ENHANCED: Enriched sources with audit trail
    evidence_sources: List[Dict[str, Any]]
    
    # ENHANCED: Evidence mapping
    dimension_evidence_map: Optional[Dict[str, Any]] = None
    
    scoring_signals: Dict[str, Any]
    base_score: float = Field(ge=0.0, le=1.0)
    avg_evidence_score: float = Field(ge=0.0, le=1.0)
    avg_retrieval_score: float = Field(ge=0.0, le=1.0)
    
    latency_ms: float
    num_chunks_analyzed: int
    
    @validator('recommendation', pre=True)
    def normalize_recommendation(cls, v):
        """Normalize recommendation to string."""
        if isinstance(v, list):
            return ' | '.join(v)
        return str(v)


class OutputFormatter:
    """Format final compliance report with Phase 5 mapping."""
    
    def __init__(self):
        """Initialize formatter with D5 and Phase 5 components."""
        self.audit_enricher = AuditEnricher()  # D5
        self.evidence_mapper = EvidenceMapper()  # Phase 5
    
    def format(
        self,
        query: str,
        framework: str,
        criterion: str,
        confidence: Dict[str, Any],
        coverage: Dict[str, Any],
        synthesis: Dict[str, Any],
        results: List[Dict[str, Any]],
        evidence_scores: List[Dict[str, Any]],
        latency: float
    ) -> Dict[str, Any]:
        """
        Assemble final compliance report with Phase 5 mapping.
        
        ENHANCED: Now includes D5 audit enrichment and Phase 5 evidence mapping.
        
        Args:
            query: Original user query
            framework: 'NAAC' or 'NBA'
            criterion: Criterion ID
            confidence: Output from ConfidenceCalculator
            coverage: Output from DimensionChecker
            synthesis: Output from ComplianceSynthesizer (validated)
            results: Phase 2 retrieval results
            evidence_scores: Output from EvidenceScorer
            latency: Total Phase 3 processing time (ms)
            
        Returns:
            Validated structured compliance report with evidence mapping
        """
        # D5: Enrich sources with audit trail
        enriched_sources = self.audit_enricher.enrich_sources(results)
        
        # Phase 5: Map evidence to dimensions
        evidence_mapping = self.evidence_mapper.map_evidence(
            results, framework, criterion
        )
        
        # Build scoring signals summary
        scoring_signals = self._build_scoring_signals(evidence_scores)
        
        # Normalize recommendation
        recommendation = synthesis.get('recommendation', '')
        if isinstance(recommendation, list):
            recommendation = ' | '.join(recommendation)
        
        # Assemble report
        report_data = {
            'run_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'query': query,
            'framework': framework,
            'criterion': criterion,
            'metric_name': coverage.get('metric_name', 'Unknown'),
            
            # Confidence and status (deterministic only)
            'confidence_score': confidence['confidence_score'],
            'compliance_status': confidence['status'],
            
            # Dimensions
            'dimensions_covered': coverage['dimensions_covered'],
            'dimensions_missing': coverage['dimensions_missing'],
            'coverage_ratio': coverage['coverage_ratio'],
            
            # Synthesis (validated by D4)
            'evidence_summary': synthesis.get('evidence_summary', ''),
            'gaps': synthesis.get('gaps', []),
            'recommendation': recommendation,
            
            # ENHANCED: D5 enriched sources with audit trail
            'evidence_sources': enriched_sources,
            
            # ENHANCED: Phase 5 evidence mapping
            'dimension_evidence_map': evidence_mapping.get('dimension_evidence_map', {}),
            
            # Scoring details
            'scoring_signals': scoring_signals,
            'base_score': confidence['base_score'],
            'avg_evidence_score': confidence['avg_evidence_score'],
            'avg_retrieval_score': confidence['avg_retrieval_score'],
            
            # Performance
            'latency_ms': round(latency, 2),
            'num_chunks_analyzed': len(results)
        }
        
        # Validate with Pydantic
        try:
            validated_report = ComplianceReport(**report_data)
            return validated_report.dict()
        except Exception as e:
            print(f"Validation error: {e}")
            # Return unvalidated report with warning
            report_data['validation_error'] = str(e)
            return report_data
    
    def _build_scoring_signals(self, evidence_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build scoring signals summary."""
        all_signals = set()
        signal_values = {
            'numeric': [],
            'entity': [],
            'keyword': [],
            'structure': []
        }
        
        for score in evidence_scores:
            signals = score.get('signals', {})
            for key in signal_values:
                if key in signals and signals[key] > 0:
                    all_signals.add(key)
                    signal_values[key].append(signals[key])
        
        # Calculate averages
        avg_signals = {}
        for key, values in signal_values.items():
            avg_signals[key] = round(sum(values) / len(values), 3) if values else 0.0
        
        return {
            'signals_detected': sorted(list(all_signals)),
            'average_values': avg_signals
        }
