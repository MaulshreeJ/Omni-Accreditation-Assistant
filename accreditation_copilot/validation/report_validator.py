"""
Report Validator - Runtime Reliability Fix
Validates audit reports before saving or returning to ensure data integrity.

This module provides defensive validation to prevent invalid data from reaching the UI.
"""

from typing import Dict, Any, List


class ReportValidationError(Exception):
    """Raised when report validation fails."""
    pass


def validate_report(report: Dict[str, Any], strict: bool = False) -> bool:
    """
    Validate audit report structure and data ranges.
    
    Args:
        report: Audit report dictionary
        strict: If True, raises exception on validation failure.
                If False, normalizes invalid values and logs warnings.
    
    Returns:
        True if valid (or normalized), False if invalid and not strict
        
    Raises:
        ReportValidationError: If strict=True and validation fails
    """
    errors = []
    warnings = []
    
    # Validate required top-level fields
    required_fields = [
        'framework',
        'criterion',
        'compliance_status',
        'confidence_score',
        'coverage_ratio',
        'evidence_sources'
    ]
    
    for field in required_fields:
        if field not in report:
            errors.append(f"Missing required field: {field}")
    
    # If critical fields missing, fail immediately
    if errors and strict:
        raise ReportValidationError(f"Report validation failed: {'; '.join(errors)}")
    elif errors:
        return False
    
    # Validate and normalize confidence_score
    if 'confidence_score' in report:
        score = report['confidence_score']
        if not isinstance(score, (int, float)):
            errors.append(f"confidence_score must be numeric, got {type(score)}")
        elif score < 0 or score > 1:
            if strict:
                errors.append(f"confidence_score out of range [0, 1]: {score}")
            else:
                # Normalize to valid range
                report['confidence_score'] = max(0.0, min(1.0, score))
                warnings.append(f"Normalized confidence_score from {score} to {report['confidence_score']}")
    
    # Validate and normalize coverage_ratio
    if 'coverage_ratio' in report:
        ratio = report['coverage_ratio']
        if not isinstance(ratio, (int, float)):
            errors.append(f"coverage_ratio must be numeric, got {type(ratio)}")
        elif ratio < 0 or ratio > 1:
            if strict:
                errors.append(f"coverage_ratio out of range [0, 1]: {ratio}")
            else:
                # Normalize to valid range
                report['coverage_ratio'] = max(0.0, min(1.0, ratio))
                warnings.append(f"Normalized coverage_ratio from {ratio} to {report['coverage_ratio']}")
    
    # Validate compliance_status
    if 'compliance_status' in report:
        valid_statuses = ['Compliant', 'Partial', 'Weak', 'Insufficient', 'No Evidence']
        if report['compliance_status'] not in valid_statuses:
            errors.append(f"Invalid compliance_status: {report['compliance_status']}")
    
    # Validate evidence_sources structure
    if 'evidence_sources' in report:
        if not isinstance(report['evidence_sources'], list):
            errors.append(f"evidence_sources must be a list, got {type(report['evidence_sources'])}")
        else:
            for idx, source in enumerate(report['evidence_sources']):
                if not isinstance(source, dict):
                    errors.append(f"evidence_sources[{idx}] must be a dict")
                    continue
                
                # Check required source fields
                required_source_fields = ['chunk_id', 'source_path', 'page_number', 'source_type']
                for field in required_source_fields:
                    if field not in source:
                        warnings.append(f"evidence_sources[{idx}] missing field: {field}")
                
                # Validate page_number is positive
                if 'page_number' in source:
                    if not isinstance(source['page_number'], int) or source['page_number'] < 0:
                        warnings.append(f"evidence_sources[{idx}] has invalid page_number: {source['page_number']}")
    
    # Validate evidence counts
    if 'evidence_count' in report and 'institution_evidence_count' in report:
        total = report['evidence_count']
        institution = report['institution_evidence_count']
        
        if not isinstance(total, int) or total < 0:
            errors.append(f"evidence_count must be non-negative integer, got {total}")
        
        if not isinstance(institution, int) or institution < 0:
            errors.append(f"institution_evidence_count must be non-negative integer, got {institution}")
        
        if institution > total:
            errors.append(f"institution_evidence_count ({institution}) cannot exceed evidence_count ({total})")
    
    # Validate dimensions_covered and dimensions_missing
    if 'dimensions_covered' in report:
        if not isinstance(report['dimensions_covered'], list):
            errors.append(f"dimensions_covered must be a list, got {type(report['dimensions_covered'])}")
    
    if 'dimensions_missing' in report:
        if not isinstance(report['dimensions_missing'], list):
            errors.append(f"dimensions_missing must be a list, got {type(report['dimensions_missing'])}")
    
    # Validate Phase 6 fields if present
    if 'dimension_grounding' in report:
        if not isinstance(report['dimension_grounding'], list):
            warnings.append(f"dimension_grounding must be a list, got {type(report['dimension_grounding'])}")
    
    if 'gaps_identified' in report:
        if not isinstance(report['gaps_identified'], list):
            warnings.append(f"gaps_identified must be a list, got {type(report['gaps_identified'])}")
        else:
            # Validate gap structure
            for idx, gap in enumerate(report['gaps_identified']):
                if not isinstance(gap, dict):
                    warnings.append(f"gaps_identified[{idx}] must be a dict")
                    continue
                
                if 'gap_type' not in gap:
                    warnings.append(f"gaps_identified[{idx}] missing gap_type")
                
                if 'severity' not in gap:
                    warnings.append(f"gaps_identified[{idx}] missing severity")
    
    if 'evidence_strength' in report:
        if not isinstance(report['evidence_strength'], dict):
            warnings.append(f"evidence_strength must be a dict, got {type(report['evidence_strength'])}")
    
    # Log warnings if any
    if warnings:
        for warning in warnings:
            print(f"[VALIDATION WARNING] {warning}")
    
    # If strict mode and errors exist, raise exception
    if errors:
        if strict:
            raise ReportValidationError(f"Report validation failed: {'; '.join(errors)}")
        else:
            for error in errors:
                print(f"[VALIDATION ERROR] {error}")
            return False
    
    return True


def validate_full_audit_report(report: Dict[str, Any], strict: bool = False) -> bool:
    """
    Validate full audit report (multiple criteria).
    
    Args:
        report: Full audit report dictionary
        strict: If True, raises exception on validation failure
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ReportValidationError: If strict=True and validation fails
    """
    errors = []
    
    # Validate top-level structure
    required_fields = ['framework', 'institution', 'audit_date', 'summary', 'criteria_results']
    
    for field in required_fields:
        if field not in report:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        if strict:
            raise ReportValidationError(f"Full audit report validation failed: {'; '.join(errors)}")
        return False
    
    # Validate summary
    if 'summary' in report:
        summary = report['summary']
        required_summary_fields = [
            'total_criteria',
            'compliant',
            'partial',
            'weak',
            'no_evidence',
            'compliance_rate'
        ]
        
        for field in required_summary_fields:
            if field not in summary:
                errors.append(f"Summary missing field: {field}")
        
        # Validate compliance_rate range
        if 'compliance_rate' in summary:
            rate = summary['compliance_rate']
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                if strict:
                    errors.append(f"Invalid compliance_rate: {rate}")
                else:
                    summary['compliance_rate'] = max(0.0, min(1.0, rate))
    
    # Validate each criterion result
    if 'criteria_results' in report:
        if not isinstance(report['criteria_results'], list):
            errors.append(f"criteria_results must be a list")
        else:
            for idx, criterion_result in enumerate(report['criteria_results']):
                try:
                    validate_report(criterion_result, strict=strict)
                except ReportValidationError as e:
                    errors.append(f"criteria_results[{idx}]: {str(e)}")
    
    if errors:
        if strict:
            raise ReportValidationError(f"Full audit report validation failed: {'; '.join(errors)}")
        return False
    
    return True


def safe_normalize_scores(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely normalize all score fields in report to [0, 1] range.
    
    This is a defensive operation that ensures no invalid scores reach the UI.
    
    Args:
        report: Audit report dictionary
        
    Returns:
        Report with normalized scores
    """
    # Normalize confidence_score
    if 'confidence_score' in report:
        report['confidence_score'] = max(0.0, min(1.0, float(report['confidence_score'])))
    
    # Normalize coverage_ratio
    if 'coverage_ratio' in report:
        report['coverage_ratio'] = max(0.0, min(1.0, float(report['coverage_ratio'])))
    
    # Normalize reranker scores in evidence sources
    if 'evidence_sources' in report and isinstance(report['evidence_sources'], list):
        for source in report['evidence_sources']:
            if isinstance(source, dict) and 'reranker_score' in source:
                source['reranker_score'] = max(0.0, min(1.0, float(source['reranker_score'])))
    
    # Normalize scores in full_report if present
    if 'full_report' in report:
        full_report = report['full_report']
        
        if 'confidence_score' in full_report:
            full_report['confidence_score'] = max(0.0, min(1.0, float(full_report['confidence_score'])))
        
        if 'coverage_ratio' in full_report:
            full_report['coverage_ratio'] = max(0.0, min(1.0, float(full_report['coverage_ratio'])))
        
        if 'base_score' in full_report:
            full_report['base_score'] = max(0.0, min(1.0, float(full_report['base_score'])))
        
        if 'avg_evidence_score' in full_report:
            full_report['avg_evidence_score'] = max(0.0, min(1.0, float(full_report['avg_evidence_score'])))
        
        if 'avg_retrieval_score' in full_report:
            full_report['avg_retrieval_score'] = max(0.0, min(1.0, float(full_report['avg_retrieval_score'])))
    
    return report
