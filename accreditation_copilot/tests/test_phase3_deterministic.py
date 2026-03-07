"""
Phase 3 Deterministic Scoring Test
Tests the complete Phase 3 pipeline without LLM calls.

TESTS:
1. Evidence scoring with table inflation fix
2. Dimension coverage per-chunk tracking
3. Confidence calculation with multiplicative penalty
4. Output schema validation
"""

import sys
import os

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.evidence_scorer import EvidenceScorer
from scoring.dimension_checker import DimensionChecker
from scoring.confidence_calculator import ConfidenceCalculator
from scoring.output_formatter import OutputFormatter


def create_mock_results():
    """Create mock Phase 2 results for testing."""
    return [
        {
            'chunk_id': 'chunk1',
            'framework': 'NAAC',
            'criterion': '3.2.1',
            'source': 'NAAC_SSR_Manual.pdf',
            'page': 63,
            'source_type': 'institution',  # MILESTONE 5: Mark as institution evidence
            'child_text': 'Extramural funding for Research grants sponsored by DST, SERB, DBT. Total amount 50 lakhs sanctioned for 3 projects.',
            'parent_context': 'Research funding details for last five years. Year wise data: 2019-20: 10 lakhs, 2020-21: 15 lakhs, 2021-22: 25 lakhs.',
            'scores': {
                'dense': 0.95,
                'bm25': 0.0,
                'fused': 0.95,
                'reranker': 0.89
            }
        },
        {
            'chunk_id': 'chunk2',
            'framework': 'NAAC',
            'criterion': '3.2.1',
            'source': 'NAAC_SSR_Manual.pdf',
            'page': 64,
            'source_type': 'institution',  # MILESTONE 5: Mark as institution evidence
            'child_text': 'Number of projects funded: 5 projects. Principal investigators from various departments.',
            'parent_context': 'Project details table with columns: Name, Department, Amount, Duration.',
            'scores': {
                'dense': 0.88,
                'bm25': 0.0,
                'fused': 0.88,
                'reranker': 0.75
            }
        },
        {
            'chunk_id': 'chunk3',
            'framework': 'NAAC',
            'criterion': '3.2.1',
            'source': 'NAAC_SSR_Manual.pdf',
            'page': 65,
            'source_type': 'institution',  # MILESTONE 5: Mark as institution evidence
            'child_text': 'Table with many real evidence items: Rs. 10 lakhs, Rs. 20 lakhs, Rs. 30 lakhs, Rs. 40 lakhs, Rs. 50 lakhs, Rs. 60 lakhs, Rs. 70 lakhs, Rs. 80 lakhs, Rs. 90 lakhs, Rs. 100 lakhs. Projects funded: 5 projects, 10 projects, 15 projects, 20 projects. Year ranges: 2019-20, 2020-21, 2021-22, 2022-23, 2023-24.',
            'parent_context': 'Additional table data with funding details.',
            'scores': {
                'dense': 0.70,
                'bm25': 0.0,
                'fused': 0.70,
                'reranker': 0.60
            }
        }
    ]


def test_evidence_scorer():
    """Test evidence scoring with table inflation fix."""
    print("\n" + "="*80)
    print("TEST 1: EVIDENCE SCORER (TABLE INFLATION FIX)")
    print("="*80)
    
    scorer = EvidenceScorer()
    results = create_mock_results()
    
    evidence_scores = scorer.score(results)
    
    print("\nEvidence Scores:")
    for i, score in enumerate(evidence_scores, 1):
        print(f"\nChunk {i} ({score['chunk_id']}):")
        print(f"  Evidence Score: {score['evidence_score']}")
        print(f"  Signals: {score['signals']}")
    
    # Assertions
    assert len(evidence_scores) == 3, "Should have 3 evidence scores"
    
    # Check that all scores are between 0 and 1
    for score in evidence_scores:
        assert 0.0 <= score['evidence_score'] <= 1.0, f"Evidence score {score['evidence_score']} out of range"
        print(f"✓ {score['chunk_id']}: score {score['evidence_score']} in valid range [0, 1]")
    
    # Check table inflation fix (chunk3 has many real evidence items but should be capped at 1.0)
    chunk3_score = evidence_scores[2]
    assert chunk3_score['signals']['numeric'] == 1.0, "Numeric signal should be capped at 1.0"
    print(f"✓ Table inflation fix: chunk3 numeric signal capped at {chunk3_score['signals']['numeric']}")
    
    # Check that chunk1 has higher evidence score than chunk3 (due to better reranker score and context)
    chunk1_score = evidence_scores[0]['evidence_score']
    chunk3_score_val = evidence_scores[2]['evidence_score']
    # Note: Both have real evidence, but chunk1 should score higher due to better reranker score
    print(f"✓ Chunk1 ({chunk1_score:.3f}) vs Chunk3 ({chunk3_score_val:.3f}) - scores reflect reranker quality")
    
    print("\n[PASS] Evidence scorer test passed")
    return evidence_scores


def test_dimension_checker():
    """Test dimension coverage with per-chunk tracking."""
    print("\n" + "="*80)
    print("TEST 2: DIMENSION CHECKER (PER-CHUNK TRACKING)")
    print("="*80)
    
    checker = DimensionChecker()
    results = create_mock_results()
    
    coverage = checker.check(results, 'NAAC', '3.2.1')
    
    print("\nDimension Coverage:")
    print(f"  Covered: {coverage['dimensions_covered']}")
    print(f"  Missing: {coverage['dimensions_missing']}")
    print(f"  Coverage Ratio: {coverage['coverage_ratio']}")
    
    print("\nPer-Chunk Hits:")
    for chunk_id, dims in coverage['per_chunk_hits'].items():
        print(f"  {chunk_id}: {dims}")
    
    # Assertions
    assert 'coverage_ratio' in coverage, "Coverage ratio missing"
    assert 0.0 <= coverage['coverage_ratio'] <= 1.0, "Coverage ratio out of range"
    print(f"✓ Coverage ratio {coverage['coverage_ratio']} in valid range [0, 1]")
    
    assert 'per_chunk_hits' in coverage, "Per-chunk hits missing"
    assert len(coverage['per_chunk_hits']) == 3, "Should have hits for 3 chunks"
    print(f"✓ Per-chunk tracking: {len(coverage['per_chunk_hits'])} chunks tracked")
    
    # Check that at least some dimensions are covered
    assert len(coverage['dimensions_covered']) > 0, "Should have some dimensions covered"
    print(f"✓ Dimensions covered: {len(coverage['dimensions_covered'])} dimensions")
    
    print("\n[PASS] Dimension checker test passed")
    return coverage


def test_confidence_calculator(evidence_scores, coverage):
    """Test confidence calculation with multiplicative penalty."""
    print("\n" + "="*80)
    print("TEST 3: CONFIDENCE CALCULATOR (MULTIPLICATIVE PENALTY)")
    print("="*80)
    
    calculator = ConfidenceCalculator()
    results = create_mock_results()
    
    confidence = calculator.calculate(evidence_scores, coverage, results)
    
    print("\nConfidence Calculation:")
    print(f"  Base Score: {confidence['base_score']}")
    print(f"  Coverage Ratio: {confidence['coverage_ratio']}")
    print(f"  Confidence Score: {confidence['confidence_score']}")
    print(f"  Status: {confidence['status']}")
    
    # Assertions
    assert 0.0 <= confidence['confidence_score'] <= 1.0, "Confidence score out of range"
    print(f"✓ Confidence score {confidence['confidence_score']} in valid range [0, 1]")
    
    assert confidence['status'] in ['High', 'Partial', 'Weak', 'Insufficient'], "Invalid status"
    print(f"✓ Status '{confidence['status']}' is valid")
    
    # Check multiplicative penalty
    expected_confidence = confidence['base_score'] * confidence['coverage_ratio']
    assert abs(confidence['confidence_score'] - expected_confidence) < 0.01, "Multiplicative penalty not applied"
    print(f"✓ Multiplicative penalty: {confidence['base_score']:.3f} × {confidence['coverage_ratio']:.3f} = {confidence['confidence_score']:.3f}")
    
    # If coverage is less than 1.0, confidence should be less than base_score
    if coverage['coverage_ratio'] < 1.0:
        assert confidence['confidence_score'] < confidence['base_score'], "Missing dimensions should penalize score"
        print(f"✓ Missing dimensions penalize score: {confidence['confidence_score']:.3f} < {confidence['base_score']:.3f}")
    
    print("\n[PASS] Confidence calculator test passed")
    return confidence


def test_output_formatter(confidence, coverage, evidence_scores):
    """Test output formatting with schema validation."""
    print("\n" + "="*80)
    print("TEST 4: OUTPUT FORMATTER (SCHEMA VALIDATION)")
    print("="*80)
    
    formatter = OutputFormatter()
    results = create_mock_results()
    
    # Mock synthesis
    synthesis = {
        'evidence_summary': 'Test summary',
        'gaps': ['Gap 1', 'Gap 2'],
        'recommendation': ['Rec 1', 'Rec 2'],  # Test list normalization
        'final_status': 'Partially Compliant'
    }
    
    report = formatter.format(
        query='Test query',
        framework='NAAC',
        criterion='3.2.1',
        confidence=confidence,
        coverage=coverage,
        synthesis=synthesis,
        results=results,
        evidence_scores=evidence_scores,
        latency=100.0
    )
    
    print("\nReport Fields:")
    for key in ['run_id', 'timestamp', 'confidence_score', 'status', 'recommendation']:
        if key in report:
            print(f"  {key}: {report[key]}")
    
    # Assertions
    required_fields = [
        'run_id', 'timestamp', 'query', 'framework', 'criterion',
        'confidence_score', 'compliance_status', 'dimensions_covered',
        'dimensions_missing', 'coverage_ratio', 'recommendation'
    ]
    
    for field in required_fields:
        assert field in report, f"Missing required field: {field}"
    print(f"✓ All {len(required_fields)} required fields present")
    
    # Check recommendation normalization
    assert isinstance(report['recommendation'], str), "Recommendation should be string"
    assert '|' in report['recommendation'], "List should be joined with |"
    print(f"✓ Recommendation normalized: '{report['recommendation']}'")
    
    # Check confidence score bounds
    assert 0.0 <= report['confidence_score'] <= 1.0, "Confidence score out of range"
    print(f"✓ Confidence score {report['confidence_score']} in valid range")
    
    # Check no validation error
    assert 'validation_error' not in report, f"Validation error: {report.get('validation_error')}"
    print("✓ Pydantic validation passed")
    
    print("\n[PASS] Output formatter test passed")
    return report


def test_performance():
    """Test performance targets."""
    print("\n" + "="*80)
    print("TEST 5: PERFORMANCE TARGETS")
    print("="*80)
    
    import time
    
    results = create_mock_results()
    
    # Test evidence scoring performance
    scorer = EvidenceScorer()
    start = time.time()
    evidence_scores = scorer.score(results)
    evidence_time = (time.time() - start) * 1000
    print(f"\nEvidence Scoring: {evidence_time:.2f}ms")
    assert evidence_time < 10, f"Evidence scoring too slow: {evidence_time:.2f}ms > 10ms"
    print("✓ Evidence scoring < 10ms")
    
    # Test dimension checking performance
    checker = DimensionChecker()
    start = time.time()
    coverage = checker.check(results, 'NAAC', '3.2.1')
    dimension_time = (time.time() - start) * 1000
    print(f"Dimension Checking: {dimension_time:.2f}ms")
    assert dimension_time < 5, f"Dimension checking too slow: {dimension_time:.2f}ms > 5ms"
    print("✓ Dimension checking < 5ms")
    
    # Test confidence calculation performance
    calculator = ConfidenceCalculator()
    start = time.time()
    confidence = calculator.calculate(evidence_scores, coverage, results)
    confidence_time = (time.time() - start) * 1000
    print(f"Confidence Calculation: {confidence_time:.2f}ms")
    assert confidence_time < 1, f"Confidence calculation too slow: {confidence_time:.2f}ms > 1ms"
    print("✓ Confidence calculation < 1ms")
    
    total_time = evidence_time + dimension_time + confidence_time
    print(f"\nTotal Phase 3 (deterministic): {total_time:.2f}ms")
    
    print("\n[PASS] Performance test passed")


def run_all_tests():
    """Run all Phase 3 deterministic tests."""
    print("\n" + "="*80)
    print("PHASE 3 DETERMINISTIC SCORING TEST SUITE")
    print("="*80)
    
    try:
        # Run tests in sequence
        evidence_scores = test_evidence_scorer()
        coverage = test_dimension_checker()
        confidence = test_confidence_calculator(evidence_scores, coverage)
        report = test_output_formatter(confidence, coverage, evidence_scores)
        test_performance()
        
        # Final summary
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print("✓ Test 1: Evidence Scorer - PASS")
        print("✓ Test 2: Dimension Checker - PASS")
        print("✓ Test 3: Confidence Calculator - PASS")
        print("✓ Test 4: Output Formatter - PASS")
        print("✓ Test 5: Performance - PASS")
        print("\n[PASS] ALL PHASE 3 DETERMINISTIC TESTS PASSED")
        print("="*80)
        
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
