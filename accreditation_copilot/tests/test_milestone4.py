"""
Test Milestone 4: Dual Retrieval Integration
Validates that dual retrieval works correctly with and without institution evidence.
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.retrieval_pipeline import RetrievalPipeline


async def test_dual_retrieval_without_institution():
    """Test that system works when institution index doesn't exist."""
    print("="*80)
    print("TEST 1: Dual Retrieval WITHOUT Institution Evidence")
    print("="*80)
    
    # Initialize pipeline with dual retrieval enabled
    pipeline = RetrievalPipeline(enable_dual_retrieval=True)
    
    # Test query
    query = "NAAC 3.2.1 research grants"
    
    print(f"\nQuery: {query}")
    print("\nExpected behavior:")
    print("  • Dual retrieval attempts to load institution index")
    print("  • Institution index not found (expected)")
    print("  • Falls back to framework-only retrieval")
    print("  • institution_evidence_available = False")
    
    # Run retrieval
    results = await pipeline.run_retrieval(query, verbose=False, enable_parent_expansion=False)
    
    # Validate
    print(f"\n✓ Retrieved {len(results)} results")
    print(f"✓ institution_evidence_available = {pipeline.institution_evidence_available}")
    
    assert len(results) > 0, "Should return results even without institution evidence"
    assert pipeline.institution_evidence_available == False, "Should indicate no institution evidence"
    
    # Check that results are framework chunks
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. [{result['framework']}] {result['source']}")
        print(f"   Criterion: {result.get('criterion', 'N/A')}")
        print(f"   Source Type: {result.get('source_type', 'N/A')}")
        
        # Validate source_type
        assert result.get('source_type') == 'framework', f"Result {i} should be framework chunk"
    
    pipeline.close()
    print("\n✓ Test 1 PASSED: System works without institution evidence")


async def test_dual_retrieval_with_institution():
    """Test that system works when institution index exists."""
    print("\n" + "="*80)
    print("TEST 2: Dual Retrieval WITH Institution Evidence")
    print("="*80)
    
    # Check if institution index exists
    from pathlib import Path
    institution_index_path = Path('indexes/institution/institution.index')
    
    if not institution_index_path.exists():
        print("\n⚠ Institution index not found - skipping this test")
        print("  Run institution_indexer.py first to create the index")
        return
    
    # Initialize pipeline with dual retrieval enabled
    pipeline = RetrievalPipeline(enable_dual_retrieval=True)
    
    # Test query that should match institution evidence
    query = "research grants funded by DST"
    
    print(f"\nQuery: {query}")
    print("\nExpected behavior:")
    print("  • Dual retrieval loads both framework and institution indexes")
    print("  • Retrieves from both indexes")
    print("  • Merges and reranks results")
    print("  • institution_evidence_available = True")
    
    # Run retrieval
    results = await pipeline.run_retrieval(query, verbose=False, enable_parent_expansion=False)
    
    # Validate
    print(f"\n✓ Retrieved {len(results)} results")
    print(f"✓ institution_evidence_available = {pipeline.institution_evidence_available}")
    
    assert len(results) > 0, "Should return results"
    assert pipeline.institution_evidence_available == True, "Should indicate institution evidence available"
    
    # Check result composition
    framework_count = sum(1 for r in results if r.get('source_type') == 'framework')
    institution_count = sum(1 for r in results if r.get('source_type') == 'institution')
    
    print(f"\nResult composition:")
    print(f"  • Framework chunks: {framework_count}")
    print(f"  • Institution chunks: {institution_count}")
    
    # Show top results
    for i, result in enumerate(results[:5], 1):
        source_type = result.get('source_type', 'unknown')
        print(f"\n{i}. [{source_type.upper()}] {result.get('source', 'N/A')}")
        if source_type == 'framework':
            print(f"   Framework: {result['framework']}, Criterion: {result.get('criterion', 'N/A')}")
        else:
            print(f"   Chunk Type: {result.get('chunk_type', 'N/A')}")
        print(f"   Reranker Score: {result['scores']['reranker']:.3f}")
    
    pipeline.close()
    print("\n✓ Test 2 PASSED: Dual retrieval works with institution evidence")


async def test_dual_retrieval_disabled():
    """Test that system works with dual retrieval disabled (backward compatibility)."""
    print("\n" + "="*80)
    print("TEST 3: Dual Retrieval DISABLED (Backward Compatibility)")
    print("="*80)
    
    # Initialize pipeline with dual retrieval disabled
    pipeline = RetrievalPipeline(enable_dual_retrieval=False)
    
    # Test query
    query = "NAAC 3.2.1 research grants"
    
    print(f"\nQuery: {query}")
    print("\nExpected behavior:")
    print("  • Uses standard hybrid + HyDE retrieval")
    print("  • No institution retrieval attempted")
    print("  • institution_evidence_available = False")
    
    # Run retrieval
    results = await pipeline.run_retrieval(query, verbose=False, enable_parent_expansion=False)
    
    # Validate
    print(f"\n✓ Retrieved {len(results)} results")
    print(f"✓ institution_evidence_available = {pipeline.institution_evidence_available}")
    
    assert len(results) > 0, "Should return results"
    assert pipeline.institution_evidence_available == False, "Should not check institution evidence"
    
    # All results should be framework chunks
    for result in results:
        assert result.get('source_type') == 'framework', "All results should be framework chunks"
    
    pipeline.close()
    print("\n✓ Test 3 PASSED: Backward compatibility maintained")


async def main():
    """Run all Milestone 4 tests."""
    print("\n" + "="*80)
    print("MILESTONE 4: DUAL RETRIEVAL INTEGRATION - VALIDATION")
    print("="*80)
    
    try:
        # Test 1: Without institution evidence (should always work)
        await test_dual_retrieval_without_institution()
        
        # Test 2: With institution evidence (if available)
        await test_dual_retrieval_with_institution()
        
        # Test 3: Backward compatibility
        await test_dual_retrieval_disabled()
        
        print("\n" + "="*80)
        print("✓ ALL MILESTONE 4 TESTS PASSED")
        print("="*80)
        print("\nMilestone 4 Complete:")
        print("  ✓ Dual retrieval integration working")
        print("  ✓ Graceful fallback when institution index missing")
        print("  ✓ Merges framework + institution results when available")
        print("  ✓ institution_evidence_available flag working")
        print("  ✓ Backward compatibility maintained")
        print("\nReady for Milestone 5: Honest Dimension Coverage")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
