"""
Cache Service for UPG System

Provides caching utilities for frequently accessed data.
Uses Django's cache framework with configurable backends.
"""

from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)

# Cache key prefixes
CACHE_PREFIX = 'upg_'
DASHBOARD_PREFIX = f'{CACHE_PREFIX}dashboard_'
STATS_PREFIX = f'{CACHE_PREFIX}stats_'
GEO_PREFIX = f'{CACHE_PREFIX}geo_'
PERMISSION_PREFIX = f'{CACHE_PREFIX}perm_'

# Cache timeouts (in seconds)
SHORT_CACHE = 60  # 1 minute
MEDIUM_CACHE = 300  # 5 minutes
LONG_CACHE = 3600  # 1 hour
GEO_CACHE = 86400  # 24 hours


def cache_key(*args):
    """Generate a cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_string = '_'.join(key_parts)
    # Use hash for long keys
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
    return key_string


def cached(timeout=MEDIUM_CACHE, prefix='', key_func=None):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds
        prefix: Key prefix for namespacing
        key_func: Optional function to generate cache key from args

    Usage:
        @cached(timeout=300, prefix='dashboard')
        def get_household_stats():
            return Household.objects.count()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_suffix = key_func(*args, **kwargs)
            else:
                cache_key_suffix = f'{func.__name__}_{cache_key(*args, *kwargs.values())}'

            full_key = f'{CACHE_PREFIX}{prefix}_{cache_key_suffix}'

            # Try to get from cache
            result = cache.get(full_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(full_key, result, timeout)
            return result
        return wrapper
    return decorator


def cached_property(timeout=MEDIUM_CACHE, prefix=''):
    """Decorator for cached class properties."""
    def decorator(func):
        @wraps(func)
        def wrapper(self):
            cache_key = f'{CACHE_PREFIX}{prefix}_{self.__class__.__name__}_{func.__name__}_{self.pk}'
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(self)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


# ============================================================================
# Dashboard Statistics Cache
# ============================================================================

def get_dashboard_stats(user, force_refresh=False):
    """
    Get cached dashboard statistics for a user.

    Returns dict with common statistics used across dashboards.
    """
    cache_key = f'{DASHBOARD_PREFIX}stats_{user.id}'

    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

    # Import models here to avoid circular imports
    from households.models import Household, HouseholdProgram
    from business_groups.models import BusinessGroup
    from savings_groups.models import BusinessSavingsGroup
    from upg_grants.models import GrantApplication
    from grants.models import SBGrant, PRGrant, HouseholdGrantApplication
    from training.models import TrainingSession
    from core.permissions import filter_queryset_by_village

    # Get user's accessible data
    households = Household.objects.all()
    households = filter_queryset_by_village(households, user)

    stats = {
        # Household stats
        'total_households': households.count(),
        'active_households': HouseholdProgram.objects.filter(
            household__in=households,
            participation_status='active'
        ).count(),
        'graduated_households': HouseholdProgram.objects.filter(
            household__in=households,
            participation_status='graduated'
        ).count(),

        # Business groups
        'total_business_groups': BusinessGroup.objects.count(),
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),

        # Savings groups
        'total_savings_groups': BusinessSavingsGroup.objects.count(),
        'active_savings_groups': BusinessSavingsGroup.objects.filter(is_active=True).count(),

        # Grants
        'sb_grants_pending': SBGrant.objects.filter(status='pending').count(),
        'sb_grants_disbursed': SBGrant.objects.filter(status='disbursed').count(),
        'pr_grants_pending': PRGrant.objects.filter(status='pending').count(),
        'pr_grants_disbursed': PRGrant.objects.filter(status='disbursed').count(),
        'household_grants_pending': HouseholdGrantApplication.objects.filter(status='pending').count(),
        'household_grants_disbursed': HouseholdGrantApplication.objects.filter(status='disbursed').count(),

        # Training
        'upcoming_trainings': TrainingSession.objects.filter(
            date__gte=timezone.now().date()
        ).count(),
        'completed_trainings': TrainingSession.objects.filter(
            status='completed'
        ).count() if hasattr(TrainingSession, 'status') else 0,

        # Timestamp
        'cached_at': timezone.now().isoformat(),
    }

    # Calculate totals
    stats['total_grants_disbursed'] = (
        stats['sb_grants_disbursed'] +
        stats['pr_grants_disbursed'] +
        stats['household_grants_disbursed']
    )

    cache.set(cache_key, stats, MEDIUM_CACHE)
    return stats


def invalidate_dashboard_cache(user_id=None):
    """
    Invalidate dashboard cache for a user or all users.
    Call this after data modifications.
    """
    if user_id:
        cache.delete(f'{DASHBOARD_PREFIX}stats_{user_id}')
    else:
        # Delete all dashboard caches (pattern-based delete)
        try:
            cache.delete_pattern(f'{DASHBOARD_PREFIX}*')
        except AttributeError:
            # Standard cache backend doesn't support patterns
            logger.warning('Cache backend does not support pattern deletion')


# ============================================================================
# Geographic Data Cache
# ============================================================================

@cached(timeout=GEO_CACHE, prefix='geo')
def get_counties_cached():
    """Get all counties (rarely changes)."""
    from core.models import County
    return list(County.objects.values('id', 'name'))


@cached(timeout=GEO_CACHE, prefix='geo')
def get_subcounties_by_county(county_id):
    """Get subcounties for a county (rarely changes)."""
    from core.models import SubCounty
    return list(SubCounty.objects.filter(county_id=county_id).values('id', 'name'))


@cached(timeout=GEO_CACHE, prefix='geo')
def get_villages_by_subcounty(subcounty_id):
    """Get villages for a subcounty (rarely changes)."""
    from core.models import Village
    return list(Village.objects.filter(subcounty_obj_id=subcounty_id).values('id', 'name'))


def invalidate_geo_cache():
    """Invalidate all geographic data cache."""
    try:
        cache.delete_pattern(f'{GEO_PREFIX}*')
    except AttributeError:
        pass


# ============================================================================
# Permission Cache
# ============================================================================

def get_user_permissions_cached(user):
    """Get cached user permissions."""
    cache_key = f'{PERMISSION_PREFIX}user_{user.id}'
    permissions = cache.get(cache_key)

    if permissions is None:
        from core.permissions import (
            can_access_module, can_edit_module, get_user_accessible_villages
        )

        modules = ['dashboard', 'households', 'programs', 'business_groups',
                   'savings_groups', 'surveys', 'training', 'grants', 'reports',
                   'settings', 'users']

        permissions = {}
        for module in modules:
            permissions[f'can_view_{module}'] = can_access_module(user, module)
            permissions[f'can_edit_{module}'] = can_edit_module(user, module)

        permissions['accessible_villages'] = get_user_accessible_villages(user)

        cache.set(cache_key, permissions, SHORT_CACHE)

    return permissions


def invalidate_user_permission_cache(user_id):
    """Invalidate permission cache when user roles change."""
    cache.delete(f'{PERMISSION_PREFIX}user_{user_id}')


# ============================================================================
# Query Optimization Helpers
# ============================================================================

def optimize_household_queryset(queryset):
    """Add common optimizations for household queries."""
    return queryset.select_related(
        'village',
        'village__subcounty_obj',
        'village__subcounty_obj__county'
    ).prefetch_related(
        'members',
        'programs__program'
    )


def optimize_business_group_queryset(queryset):
    """Add common optimizations for business group queries."""
    return queryset.prefetch_related(
        'members',
        'members__household'
    )


def optimize_savings_group_queryset(queryset):
    """Add common optimizations for savings group queries."""
    return queryset.prefetch_related(
        'members',
        'transactions'
    )


def optimize_training_queryset(queryset):
    """Add common optimizations for training queries."""
    return queryset.select_related(
        'training_module',
        'facilitator'
    ).prefetch_related(
        'attendees'
    )


def optimize_grant_queryset(queryset):
    """Add common optimizations for grant queries."""
    return queryset.select_related(
        'grant_program',
        'household',
        'household__village'
    )


# ============================================================================
# Utility Functions
# ============================================================================

def clear_all_caches():
    """Clear all UPG caches. Use with caution."""
    try:
        cache.delete_pattern(f'{CACHE_PREFIX}*')
    except AttributeError:
        cache.clear()
    logger.info('All caches cleared')


def get_cache_stats():
    """Get cache statistics if available."""
    try:
        from django.core.cache import caches
        default_cache = caches['default']

        if hasattr(default_cache, '_cache'):
            # For locmem cache
            return {
                'entries': len(default_cache._cache),
                'type': type(default_cache).__name__
            }
    except Exception as e:
        logger.warning(f'Could not get cache stats: {e}')

    return {'type': 'unknown', 'entries': 'N/A'}
