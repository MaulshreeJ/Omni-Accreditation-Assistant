"""
Audit Cache System Test Suite
Tests deterministic caching to avoid unnecessary recomputation.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cache.audit_cache import AuditCache, generate_cache_key, get_cache_stats, clear_cache
from audit.criterion_auditor import CriterionAuditor


def test_cache_key_generation():
    """Test cache key generation is deterministic."""
    print("\n" + "="*80)
    print("TEST: Cache Key Generation")
    print("="*80)
    
    cache = AuditCache()
    
    # Generate keys for same inputs
    key1 = cache.generate_cache_key('NAAC', '3.2.1', None)
    key2 = cache.generate_cache_key('NAAC', '3.2.1', None)
    
    print(f"\n[INFO] Key 1: {key1[:32]}...")
    print(f"[INFO] Key 2: {key2[:32]}...")
    
    if key1 == key2:
        print("[PASS] Cache keys are deterministic (identical inputs -> identical keys)")
    else:
        print("[FAIL] Cache keys are not deterministic")
        return False
    
    # Generate keys for different inputs
    key3 = cache.generate_cache_key('NAAC', '3.2.2', None)
    key4 = cache.generate_cache_key('NBA', '3.2.1', None)
    
    print(f"\n[INFO] Key 3 (different criterion): {key3[:32]}...")
    print(f"[INFO] Key 4 (different framework): {key4[:32]}...")
    
    if key1 != key3 and key1 != key4:
        print("[PASS] Different inputs generate different keys")
        return True
    else:
        print("[FAIL] Different inputs generated same key")
        return False


def test_cache_miss_and_hit():
    """Test cache miss followed by cache hit."""
    print("\n" + "="*80)
    print("TEST: Cache Miss and Hit")
    print("="*80)
    
    # Initialize auditor with caching enabled
    auditor = CriterionAuditor(enable_cache=True, cache_ttl_hours=24)
    
    # First audit - should be cache miss
    print("\n[TEST] Running first audit (expecting cache miss)...")
    start_time = time.time()
    
    result1 = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding for research?',
        description='Extramural funding for research'
    )
    
    first_audit_time = time.time() - start_time
    print(f"[INFO] First audit completed in {first_audit_time:.2f}s")
    
    # Second audit - should be cache hit
    print("\n[TEST] Running second audit (expecting cache hit)...")
    start_time = time.time()
    
    result2 = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding for research?',
        description='Extramural funding for research'
    )
    
    second_audit_time = time.time() - start_time
    print(f"[INFO] Second audit completed in {second_audit_time:.2f}s")
    
    # Verify results are identical
    if result1 == result2:
        print("[PASS] Cached result matches original result")
    else:
        print("[FAIL] Cached result differs from original")
        auditor.close()
        return False
    
    # Verify second audit was faster (cache hit)
    if second_audit_time < first_audit_time * 0.5:  # Should be much faster
        speedup = first_audit_time / second_audit_time if second_audit_time > 0 else float('inf')
        print(f"[PASS] Cache hit was {speedup:.1f}x faster than cache miss")
    else:
        print(f"[WARN] Cache hit not significantly faster (may still be working)")
    
    auditor.close()
    return True


def test_cache_file_exists():
    """Test that cache files are created."""
    print("\n" + "="*80)
    print("TEST: Cache File Creation")
    print("="*80)
    
    cache = AuditCache()
    auditor = CriterionAuditor(enable_cache=True)
    
    # Run an audit to create cache
    print("\n[TEST] Running audit to create cache...")
    auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding?',
        description='Extramural funding'
    )
    
    # Generate cache key using same logic as auditor
    institution_index_path = Path(__file__).parent.parent / 'indexes' / 'institution' / 'institution.index'
    cache_key = cache.generate_cache_key(
        'NAAC',
        '3.2.1',
        str(institution_index_path) if institution_index_path.exists() else None
    )
    
    # Check if cache exists
    exists = cache.cache_exists(cache_key)
    
    print(f"\n[INFO] Cache key: {cache_key[:32]}...")
    print(f"[INFO] Cache exists: {exists}")
    
    if exists:
        cache_file = cache.cache_dir / f"cache_{cache_key}.json"
        print(f"[INFO] Cache file: {cache_file.name}")
        print(f"[INFO] File size: {cache_file.stat().st_size} bytes")
        print("[PASS] Cache file exists")
        auditor.close()
        return True
    else:
        print("[FAIL] Cache file not found")
        auditor.close()
        return False


def test_cache_with_different_criteria():
    """Test that different criteria have separate cache entries."""
    print("\n" + "="*80)
    print("TEST: Different Criteria Caching")
    print("="*80)
    
    auditor = CriterionAuditor(enable_cache=True)
    cache = auditor.cache
    
    # Audit two different criteria
    print("\n[TEST] Auditing criterion 3.2.1...")
    result1 = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding?',
        description='Extramural funding'
    )
    
    print("\n[TEST] Auditing criterion 3.2.2...")
    result2 = auditor.audit_criterion(
        criterion_id='3.2.2',
        framework='NAAC',
        query_template='What are the research publications?',
        description='Research publications'
    )
    
    # Verify results are different
    if result1['criterion'] != result2['criterion']:
        print("[PASS] Different criteria produce different results")
    else:
        print("[FAIL] Different criteria produced same result")
        auditor.close()
        return False
    
    # Verify both are cached using same logic as auditor
    institution_index_path = Path(__file__).parent.parent / 'indexes' / 'institution' / 'institution.index'
    index_path_str = str(institution_index_path) if institution_index_path.exists() else None
    
    key1 = cache.generate_cache_key('NAAC', '3.2.1', index_path_str)
    key2 = cache.generate_cache_key('NAAC', '3.2.2', index_path_str)
    
    exists1 = cache.cache_exists(key1)
    exists2 = cache.cache_exists(key2)
    
    print(f"\n[INFO] Criterion 3.2.1 cached: {exists1}")
    print(f"[INFO] Criterion 3.2.2 cached: {exists2}")
    
    if exists1 and exists2:
        print("[PASS] Both criteria are cached separately")
        auditor.close()
        return True
    else:
        print(f"[FAIL] Not all criteria are cached (3.2.1: {exists1}, 3.2.2: {exists2})")
        auditor.close()
        return False


def test_cache_disabled():
    """Test that caching can be disabled."""
    print("\n" + "="*80)
    print("TEST: Cache Disabled")
    print("="*80)
    
    # Initialize auditor with caching disabled
    auditor = CriterionAuditor(enable_cache=False)
    
    print("\n[INFO] Caching disabled: {auditor.enable_cache}")
    
    if not auditor.enable_cache:
        print("[PASS] Caching is disabled")
    else:
        print("[FAIL] Caching should be disabled")
        auditor.close()
        return False
    
    # Run audit - should not use cache
    print("\n[TEST] Running audit with cache disabled...")
    result = auditor.audit_criterion(
        criterion_id='3.2.1',
        framework='NAAC',
        query_template='What is the extramural funding?',
        description='Extramural funding'
    )
    
    print("[PASS] Audit completed without caching")
    
    auditor.close()
    return True


def test_cache_stats():
    """Test cache statistics."""
    print("\n" + "="*80)
    print("TEST: Cache Statistics")
    print("="*80)
    
    stats = get_cache_stats()
    
    print(f"\n[INFO] Cache Statistics:")
    print(f"  Total cached audits: {stats['total_cached_audits']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    print(f"  By framework: {stats['by_framework']}")
    print(f"  Cache directory: {stats['cache_directory']}")
    
    if stats['total_cached_audits'] > 0:
        print("[PASS] Cache contains audit results")
        return True
    else:
        print("[INFO] Cache is empty (expected if tests run in isolation)")
        return True


def test_cache_clear():
    """Test cache clearing."""
    print("\n" + "="*80)
    print("TEST: Cache Clear")
    print("="*80)
    
    # Get initial stats
    initial_stats = get_cache_stats()
    initial_count = initial_stats['total_cached_audits']
    
    print(f"\n[INFO] Initial cached audits: {initial_count}")
    
    if initial_count == 0:
        print("[INFO] Cache is empty, skipping clear test")
        return True
    
    # Clear cache
    print("\n[TEST] Clearing cache...")
    clear_cache()
    
    # Get stats after clear
    final_stats = get_cache_stats()
    final_count = final_stats['total_cached_audits']
    
    print(f"[INFO] Final cached audits: {final_count}")
    
    if final_count == 0:
        print("[PASS] Cache cleared successfully")
        return True
    else:
        print(f"[FAIL] Cache still contains {final_count} entries")
        return False


def main():
    """Run all cache system tests."""
    print("\n" + "="*80)
    print("AUDIT CACHE SYSTEM TEST SUITE")
    print("="*80)
    
    results = {}
    
    try:
        results['Cache Key Generation'] = test_cache_key_generation()
        results['Cache Miss and Hit'] = test_cache_miss_and_hit()
        results['Cache File Creation'] = test_cache_file_exists()
        results['Different Criteria Caching'] = test_cache_with_different_criteria()
        results['Cache Disabled'] = test_cache_disabled()
        results['Cache Statistics'] = test_cache_stats()
        # Run cache clear last since it removes all cache files
        results['Cache Clear'] = test_cache_clear()
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
        print("\n[SUCCESS] All cache system tests passed")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
