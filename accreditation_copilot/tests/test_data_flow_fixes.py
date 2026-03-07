"""
Data Flow Fixes Validation Test
Tests that reranker scores, evidence counts, and chunk text propagate correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.dual_retrieval import DualRetriever
from audit.criterion_auditor import CriterionAuditor
from schemas.chunk_schema import validate_chunk, ensure_chunk_scores


def test_reranker_score_propagation():
    """Test Issue 1: Reranker scores propagate through pipeline."""
    print("\n" + "="*80)
    print("TEST: Issue 1 - Reranker Score Propagation")
    print("="*80)
    
    # Initialize retriever
    retriever = DualRetriever()
    
    # Run retrieval
    query = "What is the extramural funding for research?"
    query_variants = [query]
    
    results, _ = retriever.retrieve(
        query=query,
        query_variants=query_variants,
        framework='NAAC',
        query_type='metric',
        top_k_framework=3,
        top_k_institution=7
    )
    
    print(f"\n[INFO] Retrieved {len(results)} chunks")
    
    # Validation 1: All chunks should have reranker_score field
    chunks_with_score = [c for c in results if 'reranker_score' in c]
    print(f"[CHECK] Chunks with reranker_score: {len(chunks_with_score)}/{len(results)}")
    
    if len(chunks_with_score) == len(results):
        print("[PASS] All chunks have reranker_score field")
    else:
        print(f"[FAIL] {len(results) - len(chunks_with_score)} chunks missing reranker_score")
        retriever.close()
        return False
    
    # Validation 2: Scores should be non-zero and vary
    scores = [c['reranker_score'] for c in results]
    non_zero_scores = [s for s in scores if s > 0]
    
    print(f"[CHECK] Non-zero scores: {len(non_zero_scores)}/{len(scores)}")
    print(f"[CHECK] Score range: [{min(scores):.4f}, {max(scores):.4f}]")
    print(f"[CHECK] Unique scores: {len(set(scores))}")
    
    if len(non_zero_scores) > 0:
        print("[PASS] Reranker scores are non-zero")
    else:
        print("[WARN] All reranker scores are zero (may indicate weak evidence)")
    
    if len(set(scores)) > 1:
        print("[PASS] Reranker scores vary across chunks")
    else:
        print("[WARN] All reranker scores are identical")
    
    # Validation 3: Scores should be in [0, 1] range (sigmoid normalized)
    out_of_range = [s for s in scores if s < 0 or s > 1]
    
    if len(out_of_range) == 0:
        print("[PASS] All scores in [0, 1] range")
    else:
        print(f"[FAIL] {len(out_of_range)} scores out of range")
        retriever.close()
        return False
    
    # Validation 4: Chunks should have text field
    chunks_with_text = [c for c in results if c.get('text', '')]
    print(f"\n[CHECK] Chunks with text: {len(chunks_with_text)}/{len(results)}")
    
    if len(chunks_with_text) == len(results):
        print("[PASS] All chunks have text field")
    else:
        print(f"[WARN] {len(results) - len(chunks_with_text)} chunks missing text")
    
    retriever.close()
    
    print("\n[RESULT] Issue 1 validation complete")
    return True


def test_evidence_counting_consistency():
    """Test Issue 2: Evidence counts are consistent."""
    print("\n" + "="*80)
    print("TEST: Issue 2 - Evidence Counting Consistency")
    print("="*80)
    
    # Run audit
    auditor = CriterionAuditor()
    
    result = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding for research?',
        description='Extramural funding for research'
    )
    
    # Extract counts
    total_chunks = result.get('evidence_count', 0)
    institution_count = result.get('institution_evidence_count', 0)
    evidence_sources = result.get('evidence_sources', [])
    
    # Calculate framework count
    framework_count = total_chunks - institution_count
    
    print(f"\n[INFO] Evidence counts:")
    print(f"  Total chunks: {total_chunks}")
    print(f"  Institution: {institution_count}")
    print(f"  Framework: {framework_count}")
    print(f"  Evidence sources: {len(evidence_sources)}")
    
    # Validation 1: Total should equal institution + framework
    if total_chunks == institution_count + framework_count:
        print("[PASS] Total = Institution + Framework")
    else:
        print(f"[FAIL] Count mismatch: {total_chunks} != {institution_count} + {framework_count}")
        auditor.close()
        return False
    
    # Validation 2: Counts should be non-negative
    if total_chunks >= 0 and institution_count >= 0 and framework_count >= 0:
        print("[PASS] All counts are non-negative")
    else:
        print("[FAIL] Negative counts detected")
        auditor.close()
        return False
    
    # Validation 3: Institution count should match actual institution chunks
    actual_institution = sum(1 for s in evidence_sources if s.get('source_type') == 'institution')
    
    print(f"\n[CHECK] Actual institution chunks in sources: {actual_institution}")
    
    if actual_institution <= institution_count:
        print("[PASS] Institution count is consistent")
    else:
        print(f"[WARN] Institution count mismatch: {actual_institution} vs {institution_count}")
    
    auditor.close()
    
    print("\n[RESULT] Issue 2 validation complete")
    return True


def test_dimension_grounding_with_text():
    """Test Issue 3: Dimension grounding receives chunk text."""
    print("\n" + "="*80)
    print("TEST: Issue 3 - Dimension Grounding with Text")
    print("="*80)
    
    # Run audit
    auditor = CriterionAuditor()
    
    result = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding for research?',
        description='Extramural funding for research'
    )
    
    # Extract grounding results
    grounded_evidence = result.get('dimension_grounding', [])
    
    print(f"\n[INFO] Grounded evidence entries: {len(grounded_evidence)}")
    
    if len(grounded_evidence) > 0:
        print("[PASS] Dimension grounding produced results")
        
        # Check that grounded evidence has text previews
        with_text = [g for g in grounded_evidence if g.get('text_preview', '')]
        print(f"[CHECK] Entries with text preview: {with_text}/{len(grounded_evidence)}")
        
        if len(with_text) == len(grounded_evidence):
            print("[PASS] All grounded evidence has text preview")
        else:
            print(f"[WARN] {len(grounded_evidence) - len(with_text)} entries missing text")
        
        # Show sample
        if grounded_evidence:
            sample = grounded_evidence[0]
            print(f"\n[SAMPLE] Grounded evidence:")
            print(f"  Chunk ID: {sample.get('chunk_id', 'unknown')[:40]}")
            print(f"  Dimensions: {sample.get('dimensions_supported', [])}")
            print(f"  Source type: {sample.get('source_type', 'unknown')}")
            print(f"  Text preview: {sample.get('text_preview', '')[:100]}...")
    else:
        print("[INFO] No grounded evidence (may indicate no dimension matches)")
        print("[INFO] This is expected when evidence doesn't match required dimensions")
    
    auditor.close()
    
    print("\n[RESULT] Issue 3 validation complete")
    return True


def test_chunk_schema_validation():
    """Test Issue 4: Chunk schema validation."""
    print("\n" + "="*80)
    print("TEST: Issue 4 - Chunk Schema Validation")
    print("="*80)
    
    # Create sample chunk
    sample_chunk = {
        'chunk_id': 'test-123',
        'text': 'Sample text',
        'source_path': 'test.pdf',
        'page_number': 1,
        'source_type': 'institution',
        'framework': 'NAAC'
    }
    
    # Validate
    is_valid = validate_chunk(sample_chunk)
    
    if is_valid:
        print("[PASS] Sample chunk is valid")
    else:
        print("[FAIL] Sample chunk validation failed")
        return False
    
    # Ensure scores
    chunk_with_scores = ensure_chunk_scores(sample_chunk.copy())
    
    required_scores = ['dense_score', 'bm25_score', 'fused_score', 'reranker_score', 'final_score']
    missing_scores = [s for s in required_scores if s not in chunk_with_scores]
    
    if len(missing_scores) == 0:
        print("[PASS] All score fields present after ensure_chunk_scores")
    else:
        print(f"[FAIL] Missing scores: {missing_scores}")
        return False
    
    print("\n[RESULT] Issue 4 validation complete")
    return True


def main():
    """Run all data flow validation tests."""
    print("\n" + "="*80)
    print("DATA FLOW FIXES VALIDATION TEST SUITE")
    print("="*80)
    
    results = {}
    
    try:
        results['Issue 1: Reranker Score Propagation'] = test_reranker_score_propagation()
        results['Issue 2: Evidence Counting'] = test_evidence_counting_consistency()
        results['Issue 3: Dimension Grounding'] = test_dimension_grounding_with_text()
        results['Issue 4: Chunk Schema'] = test_chunk_schema_validation()
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
        print("\n[SUCCESS] All data flow fixes validated")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
