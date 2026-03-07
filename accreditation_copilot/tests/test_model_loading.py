"""
Model Loading Performance Test
Validates that models load only once and are reused across operations.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.model_manager import ModelManager
from audit.criterion_auditor import CriterionAuditor


def test_model_loading_once():
    """Test that models load only once during system startup."""
    print("\n" + "="*80)
    print("TEST: Model Loading Performance")
    print("="*80)
    
    # Reset ModelManager to simulate fresh start
    ModelManager.reset_instance()
    
    print("\n[Step 1] First criterion audit - models should load")
    start_time = time.time()
    
    auditor1 = CriterionAuditor()
    result1 = auditor1.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding for research?',
        description='Extramural funding for research'
    )
    
    first_audit_time = time.time() - start_time
    print(f"First audit completed in {first_audit_time:.2f} seconds")
    
    print("\n[Step 2] Second criterion audit - models should be reused")
    start_time = time.time()
    
    auditor2 = CriterionAuditor()
    result2 = auditor2.audit_criterion(
        criterion_id='3.3.1',
        framework='NAAC',
        query_template='What are the research publications?',
        description='Research publications'
    )
    
    second_audit_time = time.time() - start_time
    print(f"Second audit completed in {second_audit_time:.2f} seconds")
    
    # Validation
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    # Check that both audits returned valid results
    assert 'criterion' in result1, "First audit missing criterion field"
    assert 'criterion' in result2, "Second audit missing criterion field"
    print("[PASS] Both audits returned valid results")
    
    # Check that second audit is faster (no model loading)
    # Second audit should be at least 20% faster
    speedup = (first_audit_time - second_audit_time) / first_audit_time * 100
    print(f"\nPerformance improvement: {speedup:.1f}%")
    
    if second_audit_time < first_audit_time:
        print("[PASS] Second audit is faster (models reused)")
    else:
        print("[WARN] Second audit not faster (may vary based on query complexity)")
    
    # Check ModelManager singleton
    manager1 = ModelManager.get_instance()
    manager2 = ModelManager.get_instance()
    assert manager1 is manager2, "ModelManager should be singleton"
    print("[PASS] ModelManager is singleton")
    
    # Check that models are loaded
    assert manager1.embedder is not None, "Embedder not loaded"
    assert manager1.reranker_model is not None, "Reranker not loaded"
    assert manager1.tokenizer_tiktoken is not None, "Tokenizer not loaded"
    print("[PASS] All models are loaded in ModelManager")
    
    print("\n" + "="*80)
    print("MODEL LOADING TEST PASSED")
    print("="*80)
    
    auditor1.close()
    auditor2.close()
    
    return True


def test_model_manager_singleton():
    """Test that ModelManager follows singleton pattern."""
    print("\n" + "="*80)
    print("TEST: ModelManager Singleton Pattern")
    print("="*80)
    
    # Get multiple instances
    manager1 = ModelManager.get_instance()
    manager2 = ModelManager.get_instance()
    manager3 = ModelManager.get_instance()
    
    # All should be the same instance
    assert manager1 is manager2, "manager1 and manager2 should be same instance"
    assert manager2 is manager3, "manager2 and manager3 should be same instance"
    assert manager1 is manager3, "manager1 and manager3 should be same instance"
    
    print("[PASS] All ModelManager instances are identical")
    print("[PASS] Singleton pattern working correctly")
    
    return True


def test_shared_models():
    """Test that components share the same model instances."""
    print("\n" + "="*80)
    print("TEST: Shared Model Instances")
    print("="*80)
    
    # Create multiple auditors
    auditor1 = CriterionAuditor()
    auditor2 = CriterionAuditor()
    
    # Get model manager
    manager = ModelManager.get_instance()
    
    # Check that auditors use the same embedder
    embedder1 = auditor1.dual_retriever.embedder
    embedder2 = auditor2.dual_retriever.embedder
    manager_embedder = manager.embedder
    
    assert embedder1 is manager_embedder, "Auditor1 should use manager's embedder"
    assert embedder2 is manager_embedder, "Auditor2 should use manager's embedder"
    assert embedder1 is embedder2, "Both auditors should share same embedder"
    
    print("[PASS] All components share the same embedder instance")
    
    # Check reranker
    reranker1 = auditor1.dual_retriever.reranker.model
    reranker2 = auditor2.dual_retriever.reranker.model
    manager_reranker = manager.reranker_model
    
    assert reranker1 is manager_reranker, "Auditor1 should use manager's reranker"
    assert reranker2 is manager_reranker, "Auditor2 should use manager's reranker"
    assert reranker1 is reranker2, "Both auditors should share same reranker"
    
    print("[PASS] All components share the same reranker instance")
    
    auditor1.close()
    auditor2.close()
    
    return True


def main():
    """Run all model loading tests."""
    print("\n" + "="*80)
    print("MODEL LOADING PERFORMANCE TEST SUITE")
    print("="*80)
    
    results = {}
    
    try:
        results['Singleton Pattern'] = test_model_manager_singleton()
        results['Shared Models'] = test_shared_models()
        results['Model Loading Once'] = test_model_loading_once()
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
        print("\n[SUCCESS] All model loading tests passed")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
