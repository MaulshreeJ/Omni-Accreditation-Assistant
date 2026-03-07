"""
Cache Module
Provides deterministic caching for audit results.
"""

from cache.audit_cache import (
    AuditCache,
    generate_cache_key,
    get_cached_audit,
    save_audit_cache,
    cache_exists,
    clear_cache
)

__all__ = [
    'AuditCache',
    'generate_cache_key',
    'get_cached_audit',
    'save_audit_cache',
    'cache_exists',
    'clear_cache'
]
