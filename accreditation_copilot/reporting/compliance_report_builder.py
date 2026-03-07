"""
Compliance Report Builder - Phase 5 Component 4
Converts audit results into structured JSON reports.

Phase 6: Enhanced with evidence grounding, gap analysis, and strength scoring.
Runtime Reliability: Added report validation before saving.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from validation.report_validator import validate_full_audit_report, safe_normalize_scores


class ComplianceReportBuilder:
    """Build structured compliance reports from audit results."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report builder.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def build_report(self, audit_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build structured compliance report.
        
        Args:
            audit_report: Output from FullAuditRunner
            
        Returns:
            Structured compliance report (validated)
        """
        # Extract key information
        institution = audit_report['institution']
        framework = audit_report['framework']
        audit_date = audit_report['audit_date']
        summary = audit_report['summary']
        criteria_results = audit_report['criteria_results']
        
        # Build structured report
        report = {
            'report_metadata': {
                'report_type': 'Accreditation Compliance Audit',
                'framework': framework,
                'institution': institution,
                'audit_date': audit_date,
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0'
            },
            'executive_summary': {
                'total_criteria': summary['total_criteria'],
                'compliant': summary['compliant'],
                'partial': summary['partial'],
                'weak': summary['weak'],
                'no_evidence': summary['no_evidence'],
                'compliance_rate': summary['compliance_rate'],
                'overall_status': self._determine_overall_status(summary)
            },
            'criteria_evaluations': self._format_criteria_results(criteria_results),
            'recommendations': self._extract_recommendations(criteria_results),
            'gaps_analysis': self._extract_gaps(criteria_results),
            'evidence_summary': self._summarize_evidence(criteria_results)
        }
        
        # Validate report before returning
        try:
            validate_full_audit_report(report, strict=False)
            print("[VALIDATION] Report structure validated successfully")
        except Exception as e:
            print(f"[VALIDATION WARNING] Report validation encountered issues: {e}")
            # Continue anyway - validation is defensive, not blocking
        
        return report
    
    def save_report(
        self,
        report: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Save report to JSON file.
        
        Args:
            report: Structured compliance report
            filename: Optional custom filename
            
        Returns:
            Path to saved report
        """
        if filename is None:
            # Generate filename from metadata
            framework = report['report_metadata']['framework']
            institution = report['report_metadata']['institution'].replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{framework}_{institution}_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def _determine_overall_status(self, summary: Dict[str, Any]) -> str:
        """
        Determine overall compliance status.
        
        Args:
            summary: Audit summary
            
        Returns:
            Overall status string
        """
        compliance_rate = summary['compliance_rate']
        
        if compliance_rate >= 0.80:
            return 'Excellent'
        elif compliance_rate >= 0.60:
            return 'Good'
        elif compliance_rate >= 0.40:
            return 'Needs Improvement'
        else:
            return 'Critical'
    
    def _format_criteria_results(
        self,
        criteria_results: list
    ) -> list:
        """
        Format criteria results for report.
        
        Args:
            criteria_results: Raw criteria results
            
        Returns:
            Formatted criteria evaluations
        """
        formatted = []
        
        for result in criteria_results:
            # Skip error results
            if 'error' in result:
                formatted.append({
                    'criterion': result['criterion'],
                    'description': result['description'],
                    'status': 'Error',
                    'error_message': result['error']
                })
                continue
            
            formatted.append({
                'criterion': result['criterion'],
                'description': result['description'],
                'compliance_status': result['compliance_status'],
                'confidence_score': result['confidence_score'],
                'coverage_ratio': result['coverage_ratio'],
                'dimensions_covered': result['dimensions_covered'],
                'dimensions_missing': result['dimensions_missing'],
                'institution_evidence_available': result['institution_evidence_available'],
                'evidence_count': result['evidence_count'],
                'institution_evidence_count': result['institution_evidence_count'],
                'explanation': result['explanation'],
                'top_evidence_sources': result['evidence_sources'],
                # Phase 6 enhancements
                'dimension_grounding': result.get('dimension_grounding', []),
                'gaps_identified': result.get('gaps_identified', []),
                'evidence_strength': result.get('evidence_strength', {})
            })
        
        return formatted
    
    def _extract_recommendations(
        self,
        criteria_results: list
    ) -> list:
        """
        Extract all recommendations from criteria results.
        
        Args:
            criteria_results: Raw criteria results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for result in criteria_results:
            if 'error' in result:
                continue
            
            criterion = result['criterion']
            criterion_recs = result.get('recommendations', [])
            
            for rec in criterion_recs:
                recommendations.append({
                    'criterion': criterion,
                    'recommendation': rec
                })
        
        return recommendations
    
    def _extract_gaps(
        self,
        criteria_results: list
    ) -> list:
        """
        Extract all gaps from criteria results.
        
        Args:
            criteria_results: Raw criteria results
            
        Returns:
            List of gaps
        """
        gaps = []
        
        for result in criteria_results:
            if 'error' in result:
                continue
            
            criterion = result['criterion']
            criterion_gaps = result.get('gaps', [])
            
            for gap in criterion_gaps:
                gaps.append({
                    'criterion': criterion,
                    'gap': gap
                })
        
        return gaps
    
    def _summarize_evidence(
        self,
        criteria_results: list
    ) -> Dict[str, Any]:
        """
        Summarize evidence across all criteria.
        
        Args:
            criteria_results: Raw criteria results
            
        Returns:
            Evidence summary
        """
        total_evidence = 0
        institution_evidence = 0
        criteria_with_evidence = 0
        
        for result in criteria_results:
            if 'error' in result:
                continue
            
            total_evidence += result.get('evidence_count', 0)
            institution_evidence += result.get('institution_evidence_count', 0)
            
            if result.get('institution_evidence_available', False):
                criteria_with_evidence += 1
        
        return {
            'total_evidence_chunks': total_evidence,
            'institution_evidence_chunks': institution_evidence,
            'framework_evidence_chunks': total_evidence - institution_evidence,
            'criteria_with_institution_evidence': criteria_with_evidence,
            'criteria_without_institution_evidence': len(criteria_results) - criteria_with_evidence
        }
    
    def generate_text_summary(self, report: Dict[str, Any]) -> str:
        """
        Generate human-readable text summary.
        
        Args:
            report: Structured compliance report
            
        Returns:
            Text summary
        """
        metadata = report['report_metadata']
        summary = report['executive_summary']
        
        text = f"""
{'='*80}
ACCREDITATION COMPLIANCE REPORT
{'='*80}

Framework: {metadata['framework']}
Institution: {metadata['institution']}
Audit Date: {metadata['audit_date']}

{'='*80}
EXECUTIVE SUMMARY
{'='*80}

Total Criteria Evaluated: {summary['total_criteria']}
  Compliant: {summary['compliant']}
  Partial: {summary['partial']}
  Weak: {summary['weak']}
  No Evidence: {summary['no_evidence']}

Compliance Rate: {summary['compliance_rate']:.1%}
Overall Status: {summary['overall_status']}

{'='*80}
RECOMMENDATIONS
{'='*80}

"""
        
        recommendations = report['recommendations']
        if recommendations:
            for idx, rec in enumerate(recommendations[:10], 1):  # Top 10
                text += f"{idx}. [{rec['criterion']}] {rec['recommendation']}\n"
        else:
            text += "No recommendations available.\n"
        
        text += f"\n{'='*80}\n"
        
        return text
