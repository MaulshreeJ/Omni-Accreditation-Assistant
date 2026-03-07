"""
Full Audit CLI - Phase 5 Component 5
Command-line interface for running complete accreditation audits.

Usage:
    python run_full_audit.py --framework NAAC --institution "XYZ University"
    python run_full_audit.py --framework NBA --institution "ABC College"
"""

import sys
import argparse
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from audit.full_audit_runner import FullAuditRunner
from reporting.compliance_report_builder import ComplianceReportBuilder


def main():
    """Run full accreditation audit from command line."""
    parser = argparse.ArgumentParser(
        description='Run complete accreditation compliance audit'
    )
    
    parser.add_argument(
        '--framework',
        type=str,
        required=True,
        choices=['NAAC', 'NBA', 'naac', 'nba'],
        help='Accreditation framework (NAAC or NBA)'
    )
    
    parser.add_argument(
        '--institution',
        type=str,
        required=True,
        help='Name of the institution being audited'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports',
        help='Directory to save reports (default: reports)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress information'
    )
    
    args = parser.parse_args()
    
    # Normalize framework name
    framework = args.framework.upper()
    institution = args.institution
    
    print(f"\n{'='*80}")
    print(f"ACCREDITATION COMPLIANCE AUDIT")
    print(f"{'='*80}")
    print(f"Framework: {framework}")
    print(f"Institution: {institution}")
    print(f"Output Directory: {args.output_dir}")
    print(f"{'='*80}\n")
    
    try:
        # Initialize components
        audit_runner = FullAuditRunner()
        report_builder = ComplianceReportBuilder(output_dir=args.output_dir)
        
        # Run full audit
        print("Starting audit...\n")
        audit_report = audit_runner.run_audit(
            framework=framework,
            institution_name=institution
        )
        
        # Print summary
        audit_runner.print_summary(audit_report)
        
        # Build structured report
        print("Building compliance report...")
        compliance_report = report_builder.build_report(audit_report)
        
        # Save report
        report_path = report_builder.save_report(compliance_report)
        print(f"✓ Report saved to: {report_path}")
        
        # Generate and print text summary
        if args.verbose:
            text_summary = report_builder.generate_text_summary(compliance_report)
            print(text_summary)
        
        # Print final status
        summary = audit_report['summary']
        print(f"\n{'='*80}")
        print(f"AUDIT COMPLETE")
        print(f"{'='*80}")
        print(f"Total Criteria: {summary['total_criteria']}")
        print(f"Compliant: {summary['compliant']}")
        print(f"Partial: {summary['partial']}")
        print(f"Weak: {summary['weak']}")
        print(f"No Evidence: {summary['no_evidence']}")
        print(f"\nCompliance Rate: {summary['compliance_rate']:.1%}")
        print(f"\nReport saved to: {report_path}")
        print(f"{'='*80}\n")
        
        # Close resources
        audit_runner.close()
        
        return 0
    
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
