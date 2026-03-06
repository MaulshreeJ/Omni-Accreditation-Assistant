"""
Phase 5 Complete Validation Suite
Tests criterion mapping engine and full audit functionality.

Run this to validate Phase 5 implementation:
    python tests/test_phase5_complete.py
"""

import sys
from pathlib import Path
import subprocess

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*80)
    print(title)
    print("="*80)


def test_criterion_registry():
    """Test Phase 5.1: Criterion Registry."""
    print_header("TEST 5.1: CRITERION REGISTRY")
    
    try:
        from criteria.criterion_registry import (
            get_criteria, get_criterion, get_criterion_count, CRITERIA_REGISTRY
        )
        
        # Test NAAC criteria
        naac_criteria = get_criteria('NAAC')
        print(f"\n✓ NAAC criteria loaded: {len(naac_criteria)} criteria")
        
        # Test NBA criteria
        nba_criteria = get_criteria('NBA')
        print(f"✓ NBA criteria loaded: {len(nba_criteria)} criteria")
        
        # Test get_criterion
        criterion_321 = get_criterion('NAAC', '3.2.1')
        print(f"✓ Retrieved criterion 3.2.1: {criterion_321['description'][:50]}...")
        
        # Test criterion count
        naac_count = get_criterion_count('NAAC')
        print(f"✓ NAAC criterion count: {naac_count}")
        
        # Validate structure
        for criterion in naac_criteria:
            assert 'criterion' in criterion
            assert 'description' in criterion
            assert 'query_template' in criterion
        
        print(f"✓ All criteria have required fields")
        
        print("\n[PASS] Criterion Registry validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Criterion Registry validation failed")
        return False


def test_criterion_auditor():
    """Test Phase 5.2: Criterion Auditor."""
    print_header("TEST 5.2: CRITERION AUDITOR")
    
    try:
        from audit.criterion_auditor import CriterionAuditor
        
        # Initialize auditor
        auditor = CriterionAuditor()
        print("\n✓ Criterion auditor initialized")
        
        # Test single criterion audit
        print("\nAuditing NAAC 3.2.1...")
        result = auditor.audit_criterion(
            criterion_id='3.2.1',
            framework='NAAC',
            query_template='research funding grants from government agencies',
            description='Extramural funding for research'
        )
        
        # Validate result structure
        required_fields = [
            'framework', 'criterion', 'description', 'compliance_status',
            'confidence_score', 'coverage_ratio', 'dimensions_covered',
            'dimensions_missing', 'institution_evidence_available',
            'evidence_count', 'explanation', 'gaps', 'recommendations'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        print(f"✓ Audit completed for 3.2.1")
        print(f"  Status: {result['compliance_status']}")
        print(f"  Confidence: {result['confidence_score']:.2f}")
        print(f"  Coverage: {result['coverage_ratio']:.2f}")
        print(f"  Evidence: {result['evidence_count']} chunks")
        print(f"  Institution Evidence: {result['institution_evidence_available']}")
        
        auditor.close()
        
        print("\n[PASS] Criterion Auditor validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Criterion Auditor validation failed")
        return False


def test_full_audit_runner():
    """Test Phase 5.3: Full Audit Runner."""
    print_header("TEST 5.3: FULL AUDIT RUNNER")
    
    try:
        from audit.full_audit_runner import FullAuditRunner
        
        # Initialize runner
        runner = FullAuditRunner()
        print("\n✓ Full audit runner initialized")
        
        # Run audit for NAAC (limited to avoid long runtime)
        print("\nRunning full NAAC audit...")
        audit_report = runner.run_audit(
            framework='NAAC',
            institution_name='Test University'
        )
        
        # Validate report structure
        assert 'institution' in audit_report
        assert 'framework' in audit_report
        assert 'audit_date' in audit_report
        assert 'summary' in audit_report
        assert 'criteria_results' in audit_report
        
        summary = audit_report['summary']
        print(f"\n✓ Audit completed")
        print(f"  Total Criteria: {summary['total_criteria']}")
        print(f"  Compliant: {summary['compliant']}")
        print(f"  Partial: {summary['partial']}")
        print(f"  Weak: {summary['weak']}")
        print(f"  No Evidence: {summary['no_evidence']}")
        print(f"  Compliance Rate: {summary['compliance_rate']:.1%}")
        
        # Validate criteria results
        assert len(audit_report['criteria_results']) > 0
        print(f"✓ {len(audit_report['criteria_results'])} criteria evaluated")
        
        runner.close()
        
        print("\n[PASS] Full Audit Runner validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Full Audit Runner validation failed")
        return False


def test_report_builder():
    """Test Phase 5.4: Compliance Report Builder."""
    print_header("TEST 5.4: COMPLIANCE REPORT BUILDER")
    
    try:
        from reporting.compliance_report_builder import ComplianceReportBuilder
        from audit.full_audit_runner import FullAuditRunner
        
        # Run a quick audit
        runner = FullAuditRunner()
        audit_report = runner.run_audit(
            framework='NAAC',
            institution_name='Test University'
        )
        runner.close()
        
        # Build report
        report_builder = ComplianceReportBuilder(output_dir='reports')
        print("\n✓ Report builder initialized")
        
        compliance_report = report_builder.build_report(audit_report)
        print("✓ Compliance report built")
        
        # Validate report structure
        assert 'report_metadata' in compliance_report
        assert 'executive_summary' in compliance_report
        assert 'criteria_evaluations' in compliance_report
        assert 'recommendations' in compliance_report
        assert 'gaps_analysis' in compliance_report
        assert 'evidence_summary' in compliance_report
        
        print("✓ Report structure validated")
        
        # Save report
        report_path = report_builder.save_report(
            compliance_report,
            filename='test_phase5_report.json'
        )
        print(f"✓ Report saved to: {report_path}")
        
        # Generate text summary
        text_summary = report_builder.generate_text_summary(compliance_report)
        assert len(text_summary) > 0
        print("✓ Text summary generated")
        
        print("\n[PASS] Compliance Report Builder validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Compliance Report Builder validation failed")
        return False


def test_phase3_phase4_phase_e_stability():
    """Test that Phase 3, 4, and E still pass."""
    print_header("TEST: PHASE 3, 4, E STABILITY")
    
    try:
        print("\nRunning Phase 3 deterministic tests...")
        result = subprocess.run(
            ['python', 'tests/test_phase3_deterministic.py'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and '[PASS] ALL PHASE 3 DETERMINISTIC TESTS PASSED' in result.stdout:
            print("✓ Phase 3 tests passed")
        else:
            print("✗ Phase 3 tests failed")
            return False
        
        print("\nRunning Phase 4 complete tests...")
        result = subprocess.run(
            ['python', 'tests/test_phase4_complete.py'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 and 'ALL PHASE 4 VALIDATION TESTS PASSED' in result.stdout:
            print("✓ Phase 4 tests passed")
        else:
            print("✗ Phase 4 tests failed")
            return False
        
        print("\nRunning Phase E complete tests...")
        result = subprocess.run(
            ['python', 'tests/test_phase_e_complete.py'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 and 'ALL PHASE E VALIDATION TESTS PASSED' in result.stdout:
            print("✓ Phase E tests passed")
        else:
            print("✗ Phase E tests failed")
            return False
        
        print("\n[PASS] Phase 3, 4, E stability validated")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Stability validation failed")
        return False


def main():
    """Run all Phase 5 validation tests."""
    print_header("PHASE 5 COMPLETE VALIDATION SUITE")
    print("Testing Criterion Mapping Engine")
    
    results = []
    
    # Run all tests
    results.append(("5.1: Criterion Registry", test_criterion_registry()))
    results.append(("5.2: Criterion Auditor", test_criterion_auditor()))
    results.append(("5.3: Full Audit Runner", test_full_audit_runner()))
    results.append(("5.4: Compliance Report Builder", test_report_builder()))
    results.append(("Phase 3, 4, E Stability", test_phase3_phase4_phase_e_stability()))
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ ALL PHASE 5 VALIDATION TESTS PASSED")
        print("="*80)
        print("\nPhase 5 is complete and ready for production use.")
        print("\nKey achievements:")
        print("  • Criterion registry with NAAC and NBA criteria")
        print("  • Criterion auditor for single criterion evaluation")
        print("  • Full audit runner for complete accreditation audits")
        print("  • Compliance report builder with structured JSON output")
        print("  • CLI entrypoint for running audits")
        print("  • Phase 3, 4, and E remain stable")
        print("\nThe system has been transformed from Q&A assistant → accreditation auditor")
        print("\nUsage:")
        print("  python run_full_audit.py --framework NAAC --institution 'XYZ University'")
        return 0
    else:
        print("✗ SOME PHASE 5 VALIDATION TESTS FAILED")
        print("="*80)
        print("\nPlease review the failed tests above and fix issues.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
