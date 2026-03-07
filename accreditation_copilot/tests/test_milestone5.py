"""
Test Milestone 5: Honest Dimension Coverage
Validates that dimension coverage only counts institution chunks as evidence.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scoring.dimension_checker import DimensionChecker


def test_dimension_coverage_without_institution():
    """Test that coverage_ratio = 0 when no institution evidence exists."""
    print("="*80)
    print("TEST 1: Dimension Coverage WITHOUT Institution Evidence")
    print("="*80)
    
    checker = DimensionChecker()
    
    # Mock results with only framework chunks
    framework_results = [
        {
            'chunk_id': 'chunk1',
            'source_type': 'framework',
            'child_text': 'Number of research projects funded by DST: 15. Total funding: ₹50 lakhs.',
            'parent_context': 'Research grants from government agencies during 2020-2023.'
        },
        {
            'chunk_id': 'chunk2',
            'source_type': 'framework',
            'child_text': 'Funding agencies include DST, SERB, and ICMR.',
            'parent_context': ''
        }
    ]
    
    # Check coverage for NAAC 3.2.1
    coverage = checker.check(framework_results, 'NAAC', '3.2.1')
    
    print(f"\nFramework: NAAC")
    print(f"Criterion: 3.2.1")
    print(f"Results: {len(framework_results)} framework chunks")
    print(f"\nExpected behavior:")
    print(f"  • Only institution chunks count as evidence")
    print(f"  • No institution chunks present")
    print(f"  • coverage_ratio should be 0.0")
    print(f"  • All dimensions should be missing")
    
    print(f"\nActual results:")
    print(f"  Coverage Ratio: {coverage['coverage_ratio']}")
    print(f"  Dimensions Covered: {coverage['dimensions_covered']}")
    print(f"  Dimensions Missing: {coverage['dimensions_missing']}")
    print(f"  Institution Evidence Available: {coverage.get('institution_evidence_available', False)}")
    
    # Validate
    assert coverage['coverage_ratio'] == 0.0, "Coverage ratio should be 0 without institution evidence"
    assert len(coverage['dimensions_covered']) == 0, "No dimensions should be covered"
    assert len(coverage['dimensions_missing']) > 0, "All required dimensions should be missing"
    assert coverage.get('institution_evidence_available') == False, "Should indicate no institution evidence"
    
    print("\n✓ Test 1 PASSED: Coverage is 0 without institution evidence")


def test_dimension_coverage_with_institution():
    """Test that coverage increases when institution evidence is present."""
    print("\n" + "="*80)
    print("TEST 2: Dimension Coverage WITH Institution Evidence")
    print("="*80)
    
    checker = DimensionChecker()
    
    # Mock results with institution chunks
    institution_results = [
        {
            'chunk_id': 'inst_chunk1',
            'source_type': 'institution',
            'child_text': 'Year: 2022 | Project: AI in Education | Agency: DST | Amount: ₹24.5 Lakhs',
            'parent_context': ''
        },
        {
            'chunk_id': 'inst_chunk2',
            'source_type': 'institution',
            'child_text': 'Year: 2023 | Project: ML for Healthcare | Agency: SERB | Amount: ₹18.2 Lakhs',
            'parent_context': ''
        },
        {
            'chunk_id': 'inst_chunk3',
            'source_type': 'institution',
            'child_text': 'Year: 2021 | Project: IoT Research | Agency: ICMR | Amount: ₹30.0 Lakhs',
            'parent_context': ''
        }
    ]
    
    # Check coverage for NAAC 3.2.1
    coverage = checker.check(institution_results, 'NAAC', '3.2.1')
    
    print(f"\nFramework: NAAC")
    print(f"Criterion: 3.2.1")
    print(f"Results: {len(institution_results)} institution chunks")
    print(f"\nExpected behavior:")
    print(f"  • Institution chunks count as evidence")
    print(f"  • coverage_ratio should increase based on dimensions found")
    print(f"  • Dimensions with matching keywords should be covered")
    
    print(f"\nActual results:")
    print(f"  Coverage Ratio: {coverage['coverage_ratio']}")
    print(f"  Dimensions Covered: {coverage['dimensions_covered']}")
    print(f"  Dimensions Missing: {coverage['dimensions_missing']}")
    print(f"  Institution Evidence Available: {coverage.get('institution_evidence_available', True)}")
    print(f"  Per-Chunk Hits: {coverage['per_chunk_hits']}")
    
    # Validate
    assert coverage['coverage_ratio'] > 0.0, "Coverage ratio should be > 0 with institution evidence"
    assert len(coverage['dimensions_covered']) > 0, "Some dimensions should be covered"
    assert coverage.get('institution_evidence_available') == True, "Should indicate institution evidence available"
    assert len(coverage['per_chunk_hits']) == len(institution_results), "Should track all institution chunks"
    
    print("\n✓ Test 2 PASSED: Coverage increases with institution evidence")


def test_dimension_coverage_mixed():
    """Test that only institution chunks count, even when mixed with framework chunks."""
    print("\n" + "="*80)
    print("TEST 3: Dimension Coverage with MIXED Evidence")
    print("="*80)
    
    checker = DimensionChecker()
    
    # Mock results with both framework and institution chunks
    mixed_results = [
        {
            'chunk_id': 'framework1',
            'source_type': 'framework',
            'child_text': 'Number of research projects funded by DST: 15. Total funding: ₹50 lakhs.',
            'parent_context': 'Research grants from government agencies during 2020-2023.'
        },
        {
            'chunk_id': 'inst_chunk1',
            'source_type': 'institution',
            'child_text': 'Year: 2022 | Project: AI in Education | Agency: DST | Amount: ₹24.5 Lakhs',
            'parent_context': ''
        },
        {
            'chunk_id': 'framework2',
            'source_type': 'framework',
            'child_text': 'Funding agencies include DST, SERB, and ICMR.',
            'parent_context': ''
        },
        {
            'chunk_id': 'inst_chunk2',
            'source_type': 'institution',
            'child_text': 'Year: 2023 | Project: ML for Healthcare | Agency: SERB | Amount: ₹18.2 Lakhs',
            'parent_context': ''
        }
    ]
    
    # Check coverage for NAAC 3.2.1
    coverage = checker.check(mixed_results, 'NAAC', '3.2.1')
    
    print(f"\nFramework: NAAC")
    print(f"Criterion: 3.2.1")
    print(f"Results: {len(mixed_results)} total chunks (2 framework + 2 institution)")
    print(f"\nExpected behavior:")
    print(f"  • Only institution chunks count as evidence")
    print(f"  • Framework chunks ignored for coverage calculation")
    print(f"  • per_chunk_hits should only contain institution chunks")
    
    print(f"\nActual results:")
    print(f"  Coverage Ratio: {coverage['coverage_ratio']}")
    print(f"  Dimensions Covered: {coverage['dimensions_covered']}")
    print(f"  Institution Evidence Available: {coverage.get('institution_evidence_available', True)}")
    print(f"  Per-Chunk Hits: {coverage['per_chunk_hits']}")
    
    # Validate
    assert coverage['coverage_ratio'] > 0.0, "Coverage ratio should be > 0 with institution evidence"
    assert coverage.get('institution_evidence_available') == True, "Should indicate institution evidence available"
    
    # Verify only institution chunks are tracked
    tracked_chunks = list(coverage['per_chunk_hits'].keys())
    print(f"\n  Tracked chunks: {tracked_chunks}")
    
    for chunk_id in tracked_chunks:
        assert chunk_id.startswith('inst_'), f"Only institution chunks should be tracked, found: {chunk_id}"
    
    assert 'framework1' not in tracked_chunks, "Framework chunks should not be tracked"
    assert 'framework2' not in tracked_chunks, "Framework chunks should not be tracked"
    
    print("\n✓ Test 3 PASSED: Only institution chunks counted in mixed results")


def test_backward_compatibility():
    """Test that existing Phase 3 behavior still works (all chunks were framework)."""
    print("\n" + "="*80)
    print("TEST 4: Backward Compatibility with Phase 3")
    print("="*80)
    
    checker = DimensionChecker()
    
    # Mock Phase 3 results (all framework chunks, no source_type field)
    phase3_results = [
        {
            'chunk_id': 'chunk1',
            # No source_type field (old format)
            'child_text': 'Number of research projects funded by DST: 15. Total funding: ₹50 lakhs.',
            'parent_context': 'Research grants from government agencies during 2020-2023.'
        },
        {
            'chunk_id': 'chunk2',
            'child_text': 'Funding agencies include DST, SERB, and ICMR.',
            'parent_context': ''
        }
    ]
    
    # Check coverage for NAAC 3.2.1
    coverage = checker.check(phase3_results, 'NAAC', '3.2.1')
    
    print(f"\nFramework: NAAC")
    print(f"Criterion: 3.2.1")
    print(f"Results: {len(phase3_results)} chunks (no source_type field)")
    print(f"\nExpected behavior:")
    print(f"  • Chunks without source_type treated as non-institution")
    print(f"  • coverage_ratio should be 0.0")
    
    print(f"\nActual results:")
    print(f"  Coverage Ratio: {coverage['coverage_ratio']}")
    print(f"  Institution Evidence Available: {coverage.get('institution_evidence_available', False)}")
    
    # Validate
    assert coverage['coverage_ratio'] == 0.0, "Coverage should be 0 for old format chunks"
    assert coverage.get('institution_evidence_available') == False, "Should indicate no institution evidence"
    
    print("\n✓ Test 4 PASSED: Backward compatibility maintained")


def main():
    """Run all Milestone 5 tests."""
    print("\n" + "="*80)
    print("MILESTONE 5: HONEST DIMENSION COVERAGE - VALIDATION")
    print("="*80)
    
    try:
        # Test 1: No institution evidence
        test_dimension_coverage_without_institution()
        
        # Test 2: With institution evidence
        test_dimension_coverage_with_institution()
        
        # Test 3: Mixed evidence
        test_dimension_coverage_mixed()
        
        # Test 4: Backward compatibility
        test_backward_compatibility()
        
        print("\n" + "="*80)
        print("✓ ALL MILESTONE 5 TESTS PASSED")
        print("="*80)
        print("\nMilestone 5 Complete:")
        print("  ✓ Dimension coverage only counts institution chunks")
        print("  ✓ Framework chunks available for LLM context only")
        print("  ✓ coverage_ratio = 0 when no institution evidence")
        print("  ✓ coverage_ratio increases with institution evidence")
        print("  ✓ Per-chunk tracking only for institution chunks")
        print("  ✓ Backward compatibility maintained")
        print("\nPhase 4 Implementation Complete!")
        print("System transitioned from framework reasoning engine")
        print("to real accreditation compliance auditor.")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
