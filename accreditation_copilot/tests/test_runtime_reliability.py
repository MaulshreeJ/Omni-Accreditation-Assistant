"""
Runtime Reliability Test Suite
Tests Groq API initialization and report validation.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()

from validation.report_validator import (
    validate_report,
    validate_full_audit_report,
    safe_normalize_scores,
    ReportValidationError
)


def test_groq_initialization():
    """Test Issue 1: Groq API keys are loaded correctly."""
    print("\n" + "="*80)
    print("TEST: Issue 1 - Groq API Initialization")
    print("="*80)
    
    # Check environment variables
    groq_keys = []
    for i in range(1, 10):
        key = os.getenv(f'GROQ_API_KEY_{i}')
        if key:
            groq_keys.append(f'GROQ_API_KEY_{i}')
    
    # Check fallback single key
    if not groq_keys:
        single_key = os.getenv('GROQ_API_KEY')
        if single_key:
            groq_keys.append('GROQ_API_KEY')
    
    print(f"\n[INFO] Found {len(groq_keys)} Groq API key(s):")
    for key_name in groq_keys:
        print(f"  - {key_name}")
    
    if len(groq_keys) > 0:
        print("[PASS] Groq API keys found in environment")
        return True
    else:
        print("[FAIL] No Groq API keys found")
        print("[INFO] Set GROQ_API_KEY_1, GROQ_API_KEY_2, etc. in .env file")
        return False


def test_valid_report():
    """Test Issue 2: Valid report passes validation."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Valid Report Validation")
    print("="*80)
    
    # Create valid report
    valid_report = {
        'framework': 'NAAC',
        'criterion': '3.2.1',
        'compliance_status': 'Partial',
        'confidence_score': 0.65,
        'coverage_ratio': 0.75,
        'dimensions_covered': ['funding_amount', 'project_count'],
        'dimensions_missing': ['funding_agencies'],
        'evidence_sources': [
            {
                'chunk_id': 'test-123',
                'source_path': 'test.pdf',
                'page_number': 1,
                'source_type': 'institution',
                'reranker_score': 0.85
            }
        ],
        'evidence_count': 5,
        'institution_evidence_count': 3
    }
    
    try:
        result = validate_report(valid_report, strict=True)
        if result:
            print("[PASS] Valid report passed validation")
            return True
        else:
            print("[FAIL] Valid report failed validation")
            return False
    except Exception as e:
        print(f"[FAIL] Validation raised exception: {e}")
        return False


def test_invalid_confidence_score():
    """Test Issue 2: Invalid confidence_score is normalized."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Invalid Confidence Score Normalization")
    print("="*80)
    
    # Create report with out-of-range confidence_score
    invalid_report = {
        'framework': 'NAAC',
        'criterion': '3.2.1',
        'compliance_status': 'Partial',
        'confidence_score': 1.5,  # Invalid: > 1
        'coverage_ratio': 0.75,
        'evidence_sources': []
    }
    
    print(f"\n[INFO] Original confidence_score: {invalid_report['confidence_score']}")
    
    # Validate with strict=False (should normalize)
    try:
        result = validate_report(invalid_report, strict=False)
        normalized_score = invalid_report['confidence_score']
        
        print(f"[INFO] Normalized confidence_score: {normalized_score}")
        
        if 0 <= normalized_score <= 1:
            print("[PASS] Confidence score normalized to valid range")
            return True
        else:
            print(f"[FAIL] Normalized score still out of range: {normalized_score}")
            return False
    except Exception as e:
        print(f"[FAIL] Validation raised exception: {e}")
        return False


def test_invalid_coverage_ratio():
    """Test Issue 2: Invalid coverage_ratio is normalized."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Invalid Coverage Ratio Normalization")
    print("="*80)
    
    # Create report with negative coverage_ratio
    invalid_report = {
        'framework': 'NAAC',
        'criterion': '3.2.1',
        'compliance_status': 'Weak',
        'confidence_score': 0.5,
        'coverage_ratio': -0.1,  # Invalid: < 0
        'evidence_sources': []
    }
    
    print(f"\n[INFO] Original coverage_ratio: {invalid_report['coverage_ratio']}")
    
    # Validate with strict=False (should normalize)
    try:
        result = validate_report(invalid_report, strict=False)
        normalized_ratio = invalid_report['coverage_ratio']
        
        print(f"[INFO] Normalized coverage_ratio: {normalized_ratio}")
        
        if 0 <= normalized_ratio <= 1:
            print("[PASS] Coverage ratio normalized to valid range")
            return True
        else:
            print(f"[FAIL] Normalized ratio still out of range: {normalized_ratio}")
            return False
    except Exception as e:
        print(f"[FAIL] Validation raised exception: {e}")
        return False


def test_missing_required_fields():
    """Test Issue 2: Missing required fields are detected."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Missing Required Fields Detection")
    print("="*80)
    
    # Create report missing required fields
    incomplete_report = {
        'framework': 'NAAC',
        'criterion': '3.2.1',
        # Missing: compliance_status, confidence_score, coverage_ratio, evidence_sources
    }
    
    try:
        result = validate_report(incomplete_report, strict=True)
        print("[FAIL] Validation should have failed for missing fields")
        return False
    except ReportValidationError as e:
        print(f"[PASS] Validation correctly detected missing fields: {e}")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected exception: {e}")
        return False


def test_invalid_evidence_count():
    """Test Issue 2: Invalid evidence counts are detected."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Invalid Evidence Count Detection")
    print("="*80)
    
    # Create report with institution_count > total_count
    invalid_report = {
        'framework': 'NAAC',
        'criterion': '3.2.1',
        'compliance_status': 'Partial',
        'confidence_score': 0.5,
        'coverage_ratio': 0.5,
        'evidence_sources': [],
        'evidence_count': 5,
        'institution_evidence_count': 10  # Invalid: > evidence_count
    }
    
    try:
        result = validate_report(invalid_report, strict=True)
        print("[FAIL] Validation should have failed for invalid evidence count")
        return False
    except ReportValidationError as e:
        print(f"[PASS] Validation correctly detected invalid evidence count: {e}")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected exception: {e}")
        return False


def test_safe_normalize_scores():
    """Test Issue 2: Safe normalization of all scores."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Safe Score Normalization")
    print("="*80)
    
    # Create report with multiple out-of-range scores
    report = {
        'framework': 'NAAC',
        'criterion': '3.2.1',
        'compliance_status': 'Partial',
        'confidence_score': 1.5,
        'coverage_ratio': -0.2,
        'evidence_sources': [
            {
                'chunk_id': 'test-1',
                'source_path': 'test.pdf',
                'page_number': 1,
                'source_type': 'institution',
                'reranker_score': 2.0  # Out of range
            }
        ],
        'full_report': {
            'confidence_score': 1.8,
            'coverage_ratio': -0.5,
            'base_score': 1.2
        }
    }
    
    print("\n[INFO] Original scores:")
    print(f"  confidence_score: {report['confidence_score']}")
    print(f"  coverage_ratio: {report['coverage_ratio']}")
    print(f"  evidence reranker_score: {report['evidence_sources'][0]['reranker_score']}")
    print(f"  full_report.confidence_score: {report['full_report']['confidence_score']}")
    
    # Normalize
    normalized = safe_normalize_scores(report)
    
    print("\n[INFO] Normalized scores:")
    print(f"  confidence_score: {normalized['confidence_score']}")
    print(f"  coverage_ratio: {normalized['coverage_ratio']}")
    print(f"  evidence reranker_score: {normalized['evidence_sources'][0]['reranker_score']}")
    print(f"  full_report.confidence_score: {normalized['full_report']['confidence_score']}")
    
    # Check all scores are in [0, 1]
    all_valid = True
    
    if not (0 <= normalized['confidence_score'] <= 1):
        print(f"[FAIL] confidence_score out of range: {normalized['confidence_score']}")
        all_valid = False
    
    if not (0 <= normalized['coverage_ratio'] <= 1):
        print(f"[FAIL] coverage_ratio out of range: {normalized['coverage_ratio']}")
        all_valid = False
    
    if not (0 <= normalized['evidence_sources'][0]['reranker_score'] <= 1):
        print(f"[FAIL] reranker_score out of range: {normalized['evidence_sources'][0]['reranker_score']}")
        all_valid = False
    
    if not (0 <= normalized['full_report']['confidence_score'] <= 1):
        print(f"[FAIL] full_report.confidence_score out of range: {normalized['full_report']['confidence_score']}")
        all_valid = False
    
    if all_valid:
        print("[PASS] All scores normalized to [0, 1] range")
        return True
    else:
        print("[FAIL] Some scores still out of range")
        return False


def test_full_audit_report_validation():
    """Test Issue 2: Full audit report validation."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Full Audit Report Validation")
    print("="*80)
    
    # Create valid full audit report
    full_report = {
        'framework': 'NAAC',
        'institution': 'Test University',
        'audit_date': '2026-03-06',
        'summary': {
            'total_criteria': 10,
            'compliant': 5,
            'partial': 3,
            'weak': 2,
            'no_evidence': 0,
            'compliance_rate': 0.65
        },
        'criteria_results': [
            {
                'framework': 'NAAC',
                'criterion': '3.2.1',
                'compliance_status': 'Partial',
                'confidence_score': 0.65,
                'coverage_ratio': 0.75,
                'evidence_sources': []
            }
        ]
    }
    
    try:
        result = validate_full_audit_report(full_report, strict=True)
        if result:
            print("[PASS] Full audit report passed validation")
            return True
        else:
            print("[FAIL] Full audit report failed validation")
            return False
    except Exception as e:
        print(f"[FAIL] Validation raised exception: {e}")
        return False


def main():
    """Run all runtime reliability tests."""
    print("\n" + "="*80)
    print("RUNTIME RELIABILITY TEST SUITE")
    print("="*80)
    
    results = {}
    
    try:
        results['Issue 1: Groq Initialization'] = test_groq_initialization()
        results['Issue 2: Valid Report'] = test_valid_report()
        results['Issue 2: Invalid Confidence Score'] = test_invalid_confidence_score()
        results['Issue 2: Invalid Coverage Ratio'] = test_invalid_coverage_ratio()
        results['Issue 2: Missing Required Fields'] = test_missing_required_fields()
        results['Issue 2: Invalid Evidence Count'] = test_invalid_evidence_count()
        results['Issue 2: Safe Normalize Scores'] = test_safe_normalize_scores()
        results['Issue 2: Full Audit Report'] = test_full_audit_report_validation()
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for p in results.values() if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All runtime reliability fixes validated")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
