"""
Audit Caching System Demo
Demonstrates the performance benefits of deterministic caching.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audit.criterion_auditor import CriterionAuditor
from cache.audit_cache import get_cache_stats, clear_cache


def demo_cache_performance():
    """Demonstrate cache performance improvement."""
    print("\n" + "="*80)
    print("AUDIT CACHING SYSTEM DEMO")
    print("="*80)
    
    # Clear cache to start fresh
    print("\n[SETUP] Clearing cache to start fresh...")
    clear_cache()
    
    # Initialize auditor with caching enabled
    print("[SETUP] Initializing auditor with caching enabled...")
    auditor = CriterionAuditor(enable_cache=True, cache_ttl_hours=24)
    
    # Test criterion
    criterion_id = '3.2.1'
    framework = 'NAAC'
    query = 'What is the extramural funding for research?'
    description = 'Extramural funding for research'
    
    print(f"\n[TEST] Auditing criterion: {framework} {criterion_id}")
    print(f"[TEST] Query: {query}")
    
    # First audit - cache miss
    print("\n" + "-"*80)
    print("FIRST AUDIT (Cache Miss - Full Pipeline)")
    print("-"*80)
    
    start_time = time.time()
    result1 = auditor.audit_criterion(
        criterion_id=criterion_id,
        framework=framework,
        query_template=query,
        description=description
    )
    first_audit_time = time.time() - start_time
    
    print(f"\n[RESULT] Compliance Status: {result1['compliance_status']}")
    print(f"[RESULT] Confidence Score: {result1['confidence_score']:.2f}")
    print(f"[RESULT] Coverage Ratio: {result1['coverage_ratio']:.1%}")
    print(f"[RESULT] Evidence Sources: {len(result1['evidence_sources'])}")
    print(f"\n[TIMING] First audit completed in {first_audit_time:.2f}s")
    
    # Second audit - cache hit
    print("\n" + "-"*80)
    print("SECOND AUDIT (Cache Hit - Instant Return)")
    print("-"*80)
    
    start_time = time.time()
    result2 = auditor.audit_criterion(
        criterion_id=criterion_id,
        framework=framework,
        query_template=query,
        description=description
    )
    second_audit_time = time.time() - start_time
    
    print(f"\n[RESULT] Compliance Status: {result2['compliance_status']}")
    print(f"[RESULT] Confidence Score: {result2['confidence_score']:.2f}")
    print(f"[RESULT] Coverage Ratio: {result2['coverage_ratio']:.1%}")
    print(f"[RESULT] Evidence Sources: {len(result2['evidence_sources'])}")
    print(f"\n[TIMING] Second audit completed in {second_audit_time:.2f}s")
    
    # Performance comparison
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)
    
    speedup = first_audit_time / second_audit_time if second_audit_time > 0 else float('inf')
    time_saved = first_audit_time - second_audit_time
    
    print(f"\n[CACHE MISS] First audit: {first_audit_time:.2f}s")
    print(f"[CACHE HIT]  Second audit: {second_audit_time:.2f}s")
    print(f"\n[SPEEDUP] {speedup:.1f}x faster with cache")
    print(f"[SAVED]   {time_saved:.2f}s saved per cached audit")
    
    # Verify results are identical
    print("\n" + "="*80)
    print("RESULT VERIFICATION")
    print("="*80)
    
    if result1 == result2:
        print("\n[PASS] Cached result is identical to original result")
    else:
        print("\n[FAIL] Cached result differs from original result")
    
    # Cache statistics
    print("\n" + "="*80)
    print("CACHE STATISTICS")
    print("="*80)
    
    stats = get_cache_stats()
    print(f"\n[INFO] Total cached audits: {stats['total_cached_audits']}")
    print(f"[INFO] Total cache size: {stats['total_size_mb']} MB")
    print(f"[INFO] By framework: {stats['by_framework']}")
    print(f"[INFO] Cache directory: {stats['cache_directory']}")
    
    # Cleanup
    auditor.close()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\n[SUCCESS] Audit caching system is operational")
    print(f"[SUCCESS] Achieved {speedup:.1f}x speedup on cache hit")
    print("\n[NOTE] Cache files are stored in audit_results/ directory")
    print("[NOTE] Cache entries expire after 24 hours by default")
    print("[NOTE] Cache is automatically invalidated when institution data changes")


def demo_cache_invalidation():
    """Demonstrate cache invalidation on data changes."""
    print("\n" + "="*80)
    print("CACHE INVALIDATION DEMO")
    print("="*80)
    
    print("\n[INFO] Cache keys are based on:")
    print("  1. Framework (NAAC/NBA)")
    print("  2. Criterion ID (e.g., 3.2.1)")
    print("  3. Institution index file content hash (SHA256)")
    
    print("\n[INFO] Cache is automatically invalidated when:")
    print("  - TTL expires (default: 24 hours)")
    print("  - Institution index file content changes")
    print("  - Cache is manually cleared")
    
    print("\n[INFO] This ensures:")
    print("  - Identical inputs always return cached results")
    print("  - Different inputs generate different cache entries")
    print("  - Changes to institution data invalidate cache automatically")


def demo_cache_management():
    """Demonstrate cache management operations."""
    print("\n" + "="*80)
    print("CACHE MANAGEMENT DEMO")
    print("="*80)
    
    # Get initial stats
    stats = get_cache_stats()
    print(f"\n[INFO] Current cached audits: {stats['total_cached_audits']}")
    
    if stats['total_cached_audits'] > 0:
        print("\n[ACTION] Clearing cache...")
        clear_cache()
        
        # Verify cache is cleared
        stats = get_cache_stats()
        print(f"[INFO] Cached audits after clear: {stats['total_cached_audits']}")
        
        if stats['total_cached_audits'] == 0:
            print("[SUCCESS] Cache cleared successfully")
        else:
            print("[WARNING] Cache still contains entries")
    else:
        print("\n[INFO] Cache is already empty")


if __name__ == "__main__":
    try:
        # Run demos
        demo_cache_performance()
        demo_cache_invalidation()
        demo_cache_management()
        
        print("\n" + "="*80)
        print("ALL DEMOS COMPLETE")
        print("="*80)
        print("\n[SUCCESS] Audit caching system is fully operational")
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
