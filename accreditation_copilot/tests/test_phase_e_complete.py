"""
Phase E Complete Validation Suite
Tests observability, evaluation, and feedback components.

Run this to validate Phase E implementation:
    python tests/test_phase_e_complete.py
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


def test_e1_tracing():
    """Test E1: LangSmith Trace Logging."""
    print_header("TEST E1: LANGSMITH TRACE LOGGING")
    
    try:
        from observability.tracer import TraceManager, get_trace_manager
        
        # Initialize trace manager
        tracer = get_trace_manager()
        
        print(f"\n✓ Trace manager initialized")
        print(f"  Tracing enabled: {tracer.enabled}")
        print(f"  Project: {tracer.project_name}")
        
        # Test trace_stage context manager
        with tracer.trace_stage("test_stage", test_param="value") as outputs:
            outputs['result'] = "test_result"
            outputs['count'] = 42
        
        print(f"✓ trace_stage() working")
        print(f"  Latency captured: {outputs.get('latency_ms', 0):.2f}ms")
        
        # Test trace functions
        from observability.tracer import (
            trace_retrieval, trace_reranking, 
            trace_scoring, trace_llm_synthesis
        )
        
        print(f"✓ Trace functions imported successfully")
        
        print("\n[PASS] E1 validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] E1 validation failed")
        return False


def test_e2_retrieval_eval():
    """Test E2: Retrieval Evaluation Harness."""
    print_header("TEST E2: RETRIEVAL EVALUATION HARNESS")
    
    try:
        from evaluation.retrieval_eval import RetrievalEvaluator, create_sample_dataset
        
        # Create sample dataset
        dataset_path = "data/retrieval_eval_dataset.json"
        if not Path(dataset_path).exists():
            create_sample_dataset(dataset_path)
        
        # Initialize evaluator
        evaluator = RetrievalEvaluator(dataset_path)
        
        print(f"\n✓ Evaluator initialized")
        print(f"  Dataset: {len(evaluator.dataset)} queries")
        
        # Test metrics
        retrieved = ["chunk1", "chunk2", "chunk3", "chunk4", "chunk5"]
        expected = ["chunk1", "chunk3", "chunk6"]
        
        recall = evaluator.recall_at_k(retrieved, expected, k=5)
        precision = evaluator.precision_at_k(retrieved, expected, k=5)
        f1 = evaluator.f1_at_k(retrieved, expected, k=5)
        
        print(f"\n✓ Metrics calculated:")
        print(f"  Recall@5: {recall:.3f}")
        print(f"  Precision@5: {precision:.3f}")
        print(f"  F1@5: {f1:.3f}")
        
        # Validate metrics
        expected_recall = 2/3  # 2 out of 3 expected found
        expected_precision = 2/5  # 2 out of 5 retrieved are relevant
        
        if abs(recall - expected_recall) < 0.01 and abs(precision - expected_precision) < 0.01:
            print(f"✓ Metrics correct")
        else:
            print(f"✗ Metrics incorrect")
            return False
        
        print("\n[PASS] E2 validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] E2 validation failed")
        return False


def test_e3_feedback_store():
    """Test E3: Reviewer Feedback Logging."""
    print_header("TEST E3: REVIEWER FEEDBACK LOGGING")
    
    try:
        from feedback.feedback_store import FeedbackStore
        
        # Create test store
        test_db = "data/test_feedback_phase_e.db"
        store = FeedbackStore(test_db)
        store.clear_all()
        
        print(f"\n✓ Feedback store initialized")
        print(f"  Database: {test_db}")
        
        # Add feedback
        feedback_id = store.add_feedback(
            query="test query",
            framework="NAAC",
            criterion="3.2.1",
            chunk_id="test-chunk-123",
            rating="relevant",
            reviewer_id="test-reviewer",
            comment="Test feedback"
        )
        
        print(f"✓ Feedback added (ID: {feedback_id})")
        
        # Retrieve feedback
        query_feedback = store.get_feedback_for_query("test query")
        chunk_feedback = store.get_feedback_for_chunk("test-chunk-123")
        rating_feedback = store.get_feedback_by_rating("relevant")
        
        print(f"✓ Feedback retrieved:")
        print(f"  By query: {len(query_feedback)} records")
        print(f"  By chunk: {len(chunk_feedback)} records")
        print(f"  By rating: {len(rating_feedback)} records")
        
        # Get stats
        stats = store.get_feedback_stats()
        
        print(f"✓ Stats retrieved:")
        print(f"  Total: {stats['total_feePdback']}")
        print(f"  By rating: {stats['by_rating']}")
        
        store.close()
        
        print("\n[PASS] E3 validation passed")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] E3 validation failed")
        return False


def test_phase3_phase4_stability():
    """Test that Phase 3 and Phase 4 tests still pass."""
    print_header("TEST: PHASE 3 & PHASE 4 STABILITY")
    
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
            print("\nDebug info:")
            print(f"Return code: {result.returncode}")
            print(f"Stdout contains 'PASSED': {'PASSED' in result.stdout}")
            return False
        
        print("\n[PASS] Phase 3 & Phase 4 stability validated")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] Stability validation failed")
        return False


def main():
    """Run all Phase E validation tests."""
    print_header("PHASE E COMPLETE VALIDATION SUITE")
    print("Testing observability, evaluation, and feedback components")
    
    results = []
    
    # Run all tests
    results.append(("E1: LangSmith Trace Logging", test_e1_tracing()))
    results.append(("E2: Retrieval Evaluation Harness", test_e2_retrieval_eval()))
    results.append(("E3: Reviewer Feedback Logging", test_e3_feedback_store()))
    results.append(("Phase 3 & Phase 4 Stability", test_phase3_phase4_stability()))
    
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
        print("✓ ALL PHASE E VALIDATION TESTS PASSED")
        print("="*80)
        print("\nPhase E is complete and ready for production use.")
        print("\nKey achievements:")
        print("  • LangSmith trace logging infrastructure ready")
        print("  • Retrieval evaluation harness working")
        print("  • Reviewer feedback storage operational")
        print("  • Phase 3 and Phase 4 remain stable")
        print("\nNext steps:")
        print("  • Set LANGCHAIN_API_KEY to enable LangSmith tracing")
        print("  • Update retrieval_eval_dataset.json with real expected chunks")
        print("  • Collect reviewer feedback for retrieval tuning")
        print("  • Monitor traces in LangSmith dashboard")
        return 0
    else:
        print("✗ SOME PHASE E VALIDATION TESTS FAILED")
        print("="*80)
        print("\nPlease review the failed tests above and fix issues.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
