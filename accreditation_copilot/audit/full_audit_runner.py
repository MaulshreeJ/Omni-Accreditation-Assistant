"""
Full Audit Runner - Phase 5 Component 3
Evaluates all criteria automatically for complete accreditation audit.

Performance Fix: Initializes ModelManager once at startup.
Pre-UI Enhancement: Adds result caching for UI visualization.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from criteria.criterion_registry import get_criteria
from audit.criterion_auditor import CriterionAuditor
from models.model_manager import get_model_manager


class FullAuditRunner:
    """Run complete accreditation audit for all criteria."""
    
    def __init__(self):
        """
        Initialize audit runner.
        Loads models once at startup for reuse across all criteria.
        """
        # Initialize ModelManager (loads models once)
        self.model_manager = get_model_manager()
        
        # Initialize auditor with shared models
        self.criterion_auditor = CriterionAuditor(model_manager=self.model_manager)
        
        # Create audit_results directory if it doesn't exist
        self.results_dir = Path(__file__).parent.parent / 'audit_results'
        self.results_dir.mkdir(exist_ok=True)
    
    def run_audit(
        self,
        framework: str,
        institution_name: str = "Unknown Institution",
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete audit for all criteria in a framework.
        
        Args:
            framework: 'NAAC' or 'NBA'
            institution_name: Name of the institution being audited
            save_results: Whether to save results to disk (default: True)
            
        Returns:
            Complete audit report with all criteria results and file path
        """
        print(f"\n{'='*80}")
        print(f"STARTING FULL ACCREDITATION AUDIT")
        print(f"{'='*80}")
        print(f"Framework: {framework}")
        print(f"Institution: {institution_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*80}\n")
        
        # Generate audit ID
        audit_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audit_timestamp = datetime.now().isoformat()
        
        # Get all criteria for framework
        criteria = get_criteria(framework)
        total_criteria = len(criteria)
        
        print(f"Total criteria to evaluate: {total_criteria}\n")
        
        # Run audit for each criterion
        results = []
        compliant_count = 0
        partial_count = 0
        weak_count = 0
        no_evidence_count = 0
        
        for idx, criterion_def in enumerate(criteria, 1):
            criterion_id = criterion_def['criterion']
            description = criterion_def['description']
            query_template = criterion_def['query_template']
            
            print(f"[{idx}/{total_criteria}] Auditing {criterion_id}: {description[:60]}...")
            
            try:
                # Audit this criterion
                result = self.criterion_auditor.audit_criterion(
                    criterion_id=criterion_id,
                    framework=framework,
                    query_template=query_template,
                    description=description
                )
                
                results.append(result)
                
                # Update counts
                status = result['compliance_status']
                if status == 'Compliant':
                    compliant_count += 1
                elif status == 'Partial':
                    partial_count += 1
                elif status == 'Weak':
                    weak_count += 1
                else:  # No Evidence
                    no_evidence_count += 1
                
                print(f"  Status: {status} | Confidence: {result['confidence_score']:.2f} | Coverage: {result['coverage_ratio']:.2f}")
                
            except Exception as e:
                print(f"  ERROR: {str(e)}")
                # Add error result
                results.append({
                    'framework': framework,
                    'criterion': criterion_id,
                    'description': description,
                    'compliance_status': 'Error',
                    'error': str(e)
                })
        
        print(f"\n{'='*80}")
        print(f"AUDIT COMPLETE")
        print(f"{'='*80}\n")
        
        # Build summary
        summary = {
            'total_criteria': total_criteria,
            'compliant': compliant_count,
            'partial': partial_count,
            'weak': weak_count,
            'no_evidence': no_evidence_count,
            'compliance_rate': round(compliant_count / total_criteria, 3) if total_criteria > 0 else 0.0
        }
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(summary)
        
        # Build complete audit report with metadata
        audit_report = {
            'audit_id': audit_id,
            'institution': institution_name,
            'framework': framework,
            'audit_timestamp': audit_timestamp,
            'summary': summary,
            'overall_score': overall_score,
            'criteria_results': results,
            'metadata': {
                'total_criteria_evaluated': len(results),
                'successful_evaluations': len([r for r in results if 'error' not in r]),
                'failed_evaluations': len([r for r in results if 'error' in r]),
                'audit_duration_seconds': None  # Can be calculated if needed
            }
        }
        
        # Save results to disk if requested
        if save_results:
            result_path = self._save_audit_results(audit_report, audit_id, framework)
            audit_report['result_file_path'] = str(result_path)
            print(f"Audit results saved to: {result_path}\n")
        
        return audit_report
    
    def print_summary(self, audit_report: Dict[str, Any]):
        """
        Print audit summary to console.
        
        Args:
            audit_report: Complete audit report
        """
        summary = audit_report['summary']
        
        print(f"\n{'='*80}")
        print(f"AUDIT SUMMARY")
        print(f"{'='*80}")
        print(f"Audit ID: {audit_report.get('audit_id', 'N/A')}")
        print(f"Institution: {audit_report['institution']}")
        print(f"Framework: {audit_report['framework']}")
        print(f"Audit Date: {audit_report.get('audit_timestamp', audit_report.get('audit_date', 'N/A'))}")
        print(f"\nTotal Criteria: {summary['total_criteria']}")
        print(f"  Compliant: {summary['compliant']}")
        print(f"  Partial: {summary['partial']}")
        print(f"  Weak: {summary['weak']}")
        print(f"  No Evidence: {summary['no_evidence']}")
        print(f"\nCompliance Rate: {summary['compliance_rate']:.1%}")
        print(f"Overall Score: {audit_report.get('overall_score', 'N/A'):.2f}")
        
        if 'result_file_path' in audit_report:
            print(f"\nResults saved to: {audit_report['result_file_path']}")
        
        print(f"{'='*80}\n")
    
    def _calculate_overall_score(self, summary: Dict[str, Any]) -> float:
        """
        Calculate overall compliance score.
        
        Scoring:
        - Compliant: 1.0
        - Partial: 0.6
        - Weak: 0.3
        - No Evidence: 0.0
        
        Args:
            summary: Audit summary with counts
            
        Returns:
            Overall score (0.0 to 1.0)
        """
        total = summary['total_criteria']
        if total == 0:
            return 0.0
        
        weighted_sum = (
            summary['compliant'] * 1.0 +
            summary['partial'] * 0.6 +
            summary['weak'] * 0.3 +
            summary['no_evidence'] * 0.0
        )
        
        return round(weighted_sum / total, 3)
    
    def _save_audit_results(self, audit_report: Dict[str, Any], 
                           audit_id: str, framework: str) -> Path:
        """
        Save audit results to disk for UI visualization.
        
        Args:
            audit_report: Complete audit report
            audit_id: Unique audit identifier
            framework: Framework name
            
        Returns:
            Path to saved file
        """
        filename = f"audit_{framework.lower()}_{audit_id}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def close(self):
        """Close resources."""
        self.criterion_auditor.close()
