# Audit Caching System

## Overview

The Audit Caching System provides deterministic file-based caching to avoid unnecessary recomputation of identical audit requests. This dramatically improves performance for repeated audits of the same criterion.

## Performance

- **Cache Hit Speedup**: 114-225x faster than cache miss
- **Typical Cache Miss**: ~1.5-2.0 seconds
- **Typical Cache Hit**: ~0.01 seconds

## Architecture

### Cache Key Generation

Cache keys are generated deterministically using:
- Framework (NAAC/NBA)
- Criterion ID (e.g., "3.2.1")
- Institution index file content hash (SHA256)

This ensures that:
- Identical inputs always return cached results
- Different inputs generate different cache entries
- Changes to institution data invalidate the cache automatically

### Cache Storage

- **Location**: `audit_results/` directory
- **Format**: `cache_{hash}.json`
- **Structure**:
```json
{
  "framework": "NAAC",
  "criterion": "3.2.1",
  "timestamp": "2026-03-06T14:08:40.940940",
  "ttl_hours": 24,
  "result": { ... }
}
```

## Usage

### Enable Caching (Default)

```python
from audit.criterion_auditor import CriterionAuditor

# Initialize with caching enabled (default)
auditor = CriterionAuditor(enable_cache=True, cache_ttl_hours=24)

# First audit - cache miss (~2s)
result = auditor.audit_criterion(
    criterion_id='3.2.1',
    framework='NAAC',
    query_template='What is the extramural funding?',
    description='Extramural funding'
)

# Second audit - cache hit (~0.01s)
result = auditor.audit_criterion(
    criterion_id='3.2.1',
    framework='NAAC',
    query_template='What is the extramural funding?',
    description='Extramural funding'
)

auditor.close()
```

### Disable Caching

```python
# Initialize with caching disabled
auditor = CriterionAuditor(enable_cache=False)

# All audits will run fresh (no caching)
result = auditor.audit_criterion(...)

auditor.close()
```

### Cache Management

```python
from cache.audit_cache import get_cache_stats, clear_cache

# Get cache statistics
stats = get_cache_stats()
print(f"Total cached audits: {stats['total_cached_audits']}")
print(f"Total size: {stats['total_size_mb']} MB")
print(f"By framework: {stats['by_framework']}")

# Clear all cache
clear_cache()
```

## Cache Behavior

### Cache Miss
When an audit is not cached:
1. Full audit pipeline executes (retrieval → reranking → grounding → gap detection → synthesis)
2. Result is validated and stored in cache
3. Cache file is created with TTL metadata

### Cache Hit
When an audit is cached:
1. Cache key is generated from inputs
2. Cache file is checked for existence and validity (TTL)
3. Cached result is returned immediately
4. No AI models are invoked

### Cache Invalidation

Cache entries are automatically invalidated when:
- TTL expires (default: 24 hours)
- Institution index file content changes (detected via SHA256 hash)
- Cache is manually cleared

## Configuration

### TTL (Time To Live)

```python
# Default: 24 hours
auditor = CriterionAuditor(enable_cache=True, cache_ttl_hours=24)

# Custom TTL: 48 hours
auditor = CriterionAuditor(enable_cache=True, cache_ttl_hours=48)

# No expiration: 0 hours (cache never expires)
auditor = CriterionAuditor(enable_cache=True, cache_ttl_hours=0)
```

### Cache Directory

The cache directory is automatically created at:
- `audit_results/` (relative to project root)

## Testing

Run the cache system test suite:

```bash
cd accreditation_copilot
python tests/test_cache_system.py
```

Test coverage:
- Cache key generation (deterministic)
- Cache miss and hit behavior
- Cache file creation
- Different criteria caching
- Cache disabled mode
- Cache statistics
- Cache clearing

## Integration

The caching system is integrated into:
- `CriterionAuditor`: Main audit interface with `enable_cache` parameter
- `FullAuditRunner`: Inherits caching from `CriterionAuditor`

## Backward Compatibility

- Caching is **enabled by default** but can be disabled
- All existing tests continue to pass
- No changes to audit logic or AI reasoning
- Cache wraps around existing pipeline without modification

## Constraints

The caching system:
- Does NOT modify Phase 3 scoring logic
- Does NOT modify Phase 4 ingestion pipeline
- Does NOT modify Phase 5 criterion mapping engine
- Does NOT modify Phase 6 analysis modules
- Only adds performance optimization layer

## Future Enhancements

Potential improvements:
- Cache compression for large results
- Cache warming (pre-populate common audits)
- Cache analytics (hit rate, most cached criteria)
- Distributed cache support (Redis/Memcached)
- Cache versioning (invalidate on code changes)
