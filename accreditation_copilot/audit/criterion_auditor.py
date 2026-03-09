"""
Criterion Auditor - Phase 5 Component 2
Runs the compliance pipeline for a single criterion.

Phase 6: Enhanced with evidence grounding, gap detection, and strength scoring.
Performance Fix: Uses ModelManager for shared model instances.
Runtime Reliability: Added report validation.
Caching: Added deterministic audit caching to avoid recomputation.
FIX 8: Added timeout protection for UI reliability.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import signal
from contextlib import contextmanager

sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.query_expander import QueryExpander
from retrieval.dual_retrieval import DualRetriever
from scoring.scoring_pipeline import ScoringPipeline
from audit.audit_enricher import AuditEnricher
from analysis.evidence_grounder import EvidenceGrounder
from analysis.gap_detector import GapDetector
from scoring.evidence_strength import EvidenceStrengthScorer
from models.model_manager import get_model_manager
from validation.report_validator import validate_report, safe_normalize_scores
from cache.audit_cache import AuditCache


# FIX 8: Timeout exception
class AuditTimeoutError(Exception):
    """Raised when audit exceeds timeout limit."""
    pass


@contextmanager
def audit_timeout(seconds: int):
    """
    FIX 8: Context manager for audit timeout protection.
    
    Args:
        seconds: Timeout in seconds
        
    Raises:
        AuditTimeoutError: If audit exceeds timeout
    """
    def timeout_handler(signum, frame):
        raise AuditTimeoutError(f"Audit exceeded {seconds} second timeout")
    
    # Set up signal handler (Unix-like systems only)
    # On Windows, this will be a no-op
    try:
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    except (AttributeError, ValueError):
        # Windows doesn't support SIGALRM, just yield without timeout
        yield


class CriterionAuditor:
    """Audit a single criterion against institutional evidence."""
    
    def __init__(self, model_manager=None, enable_cache=False, cache_ttl_hours=24):
        """
        Initialize auditor with pipeline components.
        
        Args:
            model_manager: Optional ModelManager instance (for testing)
            enable_cache: Whether to enable audit caching (default: False - DISABLED for dynamic data)
            cache_ttl_hours: Cache time-to-live in hours (default: 24)
        """
        # Get shared model manager
        if model_manager is None:
            model_manager = get_model_manager()
        self.model_manager = model_manager
        
        # Initialize components with shared models
        self.query_expander = QueryExpander()
        self.dual_retriever = DualRetriever(model_manager=model_manager)
        self.scoring_pipeline = ScoringPipeline()
        self.audit_enricher = AuditEnricher()
        # Phase 6 components
        self.evidence_grounder = EvidenceGrounder()
        self.gap_detector = GapDetector()
        self.evidence_strength_scorer = EvidenceStrengthScorer()
        
        # Initialize cache
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache = AuditCache(ttl_hours=cache_ttl_hours)
        else:
            self.cache = None
    
    def audit_criterion(
        self,
        criterion_id: str,
        framework: str,
        query_template: str,
        description: str,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Audit a single criterion with caching support and timeout protection.
        
        Args:
            criterion_id: Criterion ID (e.g., '3.2.1' or 'C5')
            framework: 'NAAC' or 'NBA'
            query_template: Query template for retrieval
            description: Criterion description
            timeout_seconds: Maximum execution time (default: 30 seconds)
            
        Returns:
            Structured compliance result (from cache or fresh computation)
        """
        # FIX 8: Wrap audit execution with timeout
        try:
            with audit_timeout(timeout_seconds):
                return self._execute_audit(
                    criterion_id, framework, query_template, description
                )
        except AuditTimeoutError as e:
            print(f"[TIMEOUT] {str(e)}")
            # Return timeout response
            return {
                'framework': framework,
                'criterion': criterion_id,
                'description': description,
                'compliance_status': 'Timeout',
                'confidence_score': 0.0,
                'coverage_ratio': 0.0,
                'dimensions_covered': [],
                'dimensions_missing': [],
                'institution_evidence_available': False,
                'evidence_count': 0,
                'institution_evidence_count': 0,
                'explanation': f'Audit exceeded {timeout_seconds} second timeout',
                'gaps': ['Audit timed out - please retry or contact support'],
                'recommendations': ['Retry the audit', 'Check system performance'],
                'evidence_sources': [],
                'dimension_grounding': [],
                'gaps_identified': [],
                'evidence_strength': {},
                'full_report': {}
            }
    
    def _execute_audit(
        self,
        criterion_id: str,
        framework: str,
        query_template: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Internal method to execute audit logic.
        
        Args:
            criterion_id: Criterion ID
            framework: Framework name
            query_template: Query template
            description: Criterion description
            
        Returns:
            Audit result
        """
        # Check cache if enabled
        if self.enable_cache and self.cache:
            # Generate cache key based on framework, criterion, and institution content
            institution_index_path = Path(__file__).parent.parent / 'indexes' / 'institution' / 'institution.index'
            cache_key = self.cache.generate_cache_key(
                framework=framework,
                criterion=criterion_id,
                institution_index_path=str(institution_index_path) if institution_index_path.exists() else None
            )
            
            # Try to get cached result
            cached_result = self.cache.get_cached_audit(cache_key)
            if cached_result is not None:
                return cached_result
            
            print(f"[CACHE MISS] Running new audit for {framework} {criterion_id}")
        
        # Step 1: Expand query
        query_variants = self.query_expander.expand_query(
            query_template,
            framework
        )
        
        # Step 2: Run dual retrieval (framework + institution)
        retrieval_results, institution_evidence_available = self.dual_retriever.retrieve(
            query=query_template,
            query_variants=query_variants,
            framework=framework,
            query_type='metric',  # Default to metric for criterion evaluation
            top_k_framework=3,
            top_k_institution=7
        )
        
        # Step 3: Run Phase 3 scoring pipeline
        compliance_report = self.scoring_pipeline.process(
            query=query_template,
            framework=framework,
            criterion=criterion_id,
            retrieval_results=retrieval_results
        )
        
        # Step 4: Enrich with audit trail
        enriched_sources = self.audit_enricher.enrich_sources(retrieval_results)
        
        # Step 5: Extract key metrics (handle both nested and flat structures)
        confidence_score = compliance_report.get('confidence_score', 
                                                compliance_report.get('confidence', {}).get('overall_confidence', 0.0))
        coverage_ratio = compliance_report.get('coverage_ratio',
                                              compliance_report.get('coverage', {}).get('coverage_ratio', 0.0))
        dimensions_covered = compliance_report.get('dimensions_covered',
                                                  compliance_report.get('coverage', {}).get('dimensions_covered', []))
        dimensions_missing = compliance_report.get('dimensions_missing',
                                                  compliance_report.get('coverage', {}).get('dimensions_missing', []))
        
        # Step 6: Determine compliance status
        compliance_status = self._determine_compliance_status(
            confidence_score,
            coverage_ratio,
            institution_evidence_available
        )
        
        # Step 7: Extract synthesis (handle both nested and flat structures)
        synthesis = compliance_report.get('synthesis', {})
        explanation = compliance_report.get('evidence_summary', synthesis.get('explanation', 'No explanation available'))
        gaps = compliance_report.get('gaps', synthesis.get('gaps', []))
        recommendations = compliance_report.get('recommendation', synthesis.get('recommendations', []))
        if isinstance(recommendations, str):
            recommendations = [recommendations] if recommendations else []
        
        # Step 8: Build structured result
        result = {
            'framework': framework,
            'criterion': criterion_id,
            'description': description,
            'compliance_status': compliance_status,
            'confidence_score': round(confidence_score, 3),
            'coverage_ratio': round(coverage_ratio, 3),
            'dimensions_covered': dimensions_covered,
            'dimensions_missing': dimensions_missing,
            'institution_evidence_available': institution_evidence_available,
            'evidence_count': len(retrieval_results),
            'institution_evidence_count': sum(1 for r in retrieval_results if self._is_institution_chunk(r)),
            'explanation': explanation,
            'gaps': gaps,
            'recommendations': recommendations,
            'evidence_sources': enriched_sources[:5],  # Top 5 sources
            'full_report': compliance_report
        }
        
        # Phase 6: Add enhanced analysis
        coverage = compliance_report.get('coverage', {})
        confidence = compliance_report.get('confidence', {})
        per_chunk_hits = coverage.get('per_chunk_hits', {})
        
        # Evidence grounding
        grounded_evidence = self.evidence_grounder.ground_evidence(
            retrieval_results,
            per_chunk_hits
        )
        result['dimension_grounding'] = grounded_evidence[:10]  # Top 10
        
        # Gap detection
        detected_gaps = self.gap_detector.detect_gaps(
            coverage,
            confidence,
            institution_evidence_available
        )
        result['gaps_identified'] = self.gap_detector.prioritize_gaps(detected_gaps)
        
        # Evidence strength scoring
        evidence_scores_dict = compliance_report.get('evidence_scores', {})
        strength_analysis = self.evidence_strength_scorer.score_evidence_strength(
            retrieval_results,
            per_chunk_hits,
            evidence_scores_dict
        )
        result['evidence_strength'] = strength_analysis
        
        # Validate and normalize report before returning
        try:
            result = safe_normalize_scores(result)
            validate_report(result, strict=False)
        except Exception as e:
            print(f"[VALIDATION WARNING] Report validation issue for {criterion_id}: {e}")
            # Continue anyway - validation is defensive
        
        # Save to cache if enabled
        if self.enable_cache and self.cache:
            self.cache.save_audit_cache(
                cache_key=cache_key,
                report=result,
                framework=framework,
                criterion=criterion_id
            )
        
        return result
    
    def _determine_compliance_status(
        self,
        confidence_score: float,
        coverage_ratio: float,
        institution_evidence_available: bool
    ) -> str:
        """
        Determine compliance status based on metrics.
        
        Args:
            confidence_score: Overall confidence (0-1)
            coverage_ratio: Dimension coverage (0-1)
            institution_evidence_available: Whether institution evidence exists
            
        Returns:
            'Compliant', 'Partial', 'Weak', or 'No Evidence'
        """
        if not institution_evidence_available:
            return 'No Evidence'
        
        # Combined score: average of confidence and coverage
        combined_score = (confidence_score + coverage_ratio) / 2
        
        if combined_score >= 0.75:
            return 'Compliant'
        elif combined_score >= 0.50:
            return 'Partial'
        else:
            return 'Weak'
    
    def _is_institution_chunk(self, result: Dict[str, Any]) -> bool:
        """
        Check if a result is from institutional evidence.
        
        Args:
            result: Retrieval result
            
        Returns:
            True if from institution index
        """
        # Check source_type metadata from dual_retrieval
        # This is set during retrieval based on database metadata
        return result.get('source_type') == 'institution'
    
    def close(self):
        """Close resources."""
        self.dual_retriever.close()
        self.evidence_grounder.close()
