"""
Centralized Permission System for UPG System.
Handles both built-in roles and custom roles with module-level and geographic permissions.
"""

from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# =============================================================================
# Module Permission Mapping
# =============================================================================

# Maps URL app names to module permission keys
MODULE_MAP = {
    'dashboard': 'dashboard',
    'programs': 'programs',
    'households': 'households',
    'business_groups': 'business_groups',
    'savings_groups': 'savings_groups',
    'surveys': 'surveys',
    'forms': 'surveys',
    'training': 'training',
    'upg_grants': 'grants',
    'grants': 'grants',
    'reports': 'reports',
    'settings': 'settings',
    'settings_module': 'settings',
    'accounts': 'users',
    'core': 'dashboard',
}

# Built-in role permissions (for backwards compatibility)
BUILTIN_ROLE_PERMISSIONS = {
    'ict_admin': {
        'dashboard': 'full', 'programs': 'full', 'households': 'full',
        'business_groups': 'full', 'savings_groups': 'full', 'surveys': 'full',
        'training': 'full', 'grants': 'full', 'reports': 'full',
        'settings': 'full', 'users': 'full', 'audit_logs': 'full', 'kobo': 'full'
    },
    'program_manager': {
        'dashboard': 'full', 'programs': 'full', 'households': 'full',
        'business_groups': 'full', 'savings_groups': 'full', 'surveys': 'full',
        'training': 'full', 'grants': 'full', 'reports': 'full',
        'settings': 'read', 'users': 'read', 'audit_logs': 'read', 'kobo': 'read'
    },
    'me_staff': {
        'dashboard': 'full', 'programs': 'read', 'households': 'full',
        'business_groups': 'full', 'savings_groups': 'full', 'surveys': 'full',
        'training': 'full', 'grants': 'read', 'reports': 'full',
        'settings': 'read', 'users': 'none', 'audit_logs': 'full', 'kobo': 'read'
    },
    'field_associate': {
        'dashboard': 'full', 'programs': 'read', 'households': 'full',
        'business_groups': 'full', 'savings_groups': 'full', 'surveys': 'read',
        'training': 'full', 'grants': 'read', 'reports': 'read',
        'settings': 'none', 'users': 'none', 'audit_logs': 'none', 'kobo': 'none'
    },
    'mentor': {
        'dashboard': 'full', 'programs': 'read', 'households': 'full',
        'business_groups': 'full', 'savings_groups': 'full', 'surveys': 'read',
        'training': 'full', 'grants': 'read', 'reports': 'read',
        'settings': 'none', 'users': 'none', 'audit_logs': 'none', 'kobo': 'none'
    },
    'county_executive': {
        'dashboard': 'full', 'programs': 'read', 'households': 'read',
        'business_groups': 'read', 'savings_groups': 'read', 'surveys': 'read',
        'training': 'read', 'grants': 'read', 'reports': 'full',
        'settings': 'none', 'users': 'none', 'audit_logs': 'read', 'kobo': 'none'
    },
    'county_assembly': {
        'dashboard': 'full', 'programs': 'read', 'households': 'read',
        'business_groups': 'read', 'savings_groups': 'read', 'surveys': 'read',
        'training': 'read', 'grants': 'read', 'reports': 'full',
        'settings': 'none', 'users': 'none', 'audit_logs': 'none', 'kobo': 'none'
    },
    'beneficiary': {
        'dashboard': 'read', 'programs': 'none', 'households': 'none',
        'business_groups': 'none', 'savings_groups': 'none', 'surveys': 'none',
        'training': 'none', 'grants': 'none', 'reports': 'none',
        'settings': 'none', 'users': 'none', 'audit_logs': 'none', 'kobo': 'none'
    },
}


# =============================================================================
# Permission Check Functions
# =============================================================================

def get_user_module_permission(user, module):
    """
    Get user's permission level for a specific module.

    Returns: 'full', 'read', or 'none'
    """
    if not user or not user.is_authenticated:
        return 'none'

    # Superusers have full access to everything
    if user.is_superuser:
        return 'full'

    # Check for custom role first
    if hasattr(user, 'role') and user.role == 'custom':
        if hasattr(user, 'custom_role') and user.custom_role:
            custom_role = user.custom_role
            if custom_role.is_active:
                return custom_role.has_permission(module, 'read')  # Returns level or False

    # Fall back to built-in role permissions
    user_role = getattr(user, 'role', None)
    if user_role and user_role in BUILTIN_ROLE_PERMISSIONS:
        return BUILTIN_ROLE_PERMISSIONS[user_role].get(module, 'none')

    return 'none'


def has_module_access(user, module, required_level='read'):
    """
    Check if user has required access level for a module.

    Args:
        user: User object
        module: Module key (e.g., 'households', 'grants')
        required_level: 'read' or 'full'

    Returns: True if access granted, False otherwise
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    user_permission = get_user_module_permission(user, module)

    if user_permission == 'none':
        return False

    if required_level == 'read':
        return user_permission in ['read', 'full']

    if required_level == 'full':
        return user_permission == 'full'

    return False


def can_access_module(user, module):
    """Shortcut for read access check."""
    return has_module_access(user, module, 'read')


def can_edit_module(user, module):
    """Shortcut for full (write) access check."""
    return has_module_access(user, module, 'full')


# =============================================================================
# Geographic Permission Functions
# =============================================================================

def get_user_accessible_villages(user):
    """
    Get list of village IDs accessible to a user based on role.

    Returns:
        list: List of village IDs, or None for unrestricted access
    """
    if not user or not user.is_authenticated:
        return []

    # Superusers and certain roles see all
    if user.is_superuser:
        return None  # None means unrestricted

    user_role = getattr(user, 'role', None)

    # Admin roles see everything
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return None

    # Check for custom role with geographic restrictions
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active:
            scope = custom_role.geographic_scope

            if scope == 'all':
                return None

            if scope == 'county':
                from core.models import Village
                counties = custom_role.allowed_counties or []
                return list(Village.objects.filter(
                    subcounty_obj__county__name__in=counties
                ).values_list('id', flat=True))

            if scope == 'subcounty':
                from core.models import Village
                subcounties = custom_role.allowed_subcounties or []
                return list(Village.objects.filter(
                    subcounty_obj__name__in=subcounties
                ).values_list('id', flat=True))

            if scope == 'villages':
                return custom_role.allowed_villages or []

    # Field associates see supervised mentors' villages
    if user_role == 'field_associate':
        from accounts.models import UserProfile
        supervised_profiles = UserProfile.objects.filter(supervisor=user)
        village_ids = set()
        for profile in supervised_profiles:
            if hasattr(profile, 'assigned_villages'):
                village_ids.update(profile.assigned_villages.values_list('id', flat=True))
        return list(village_ids) if village_ids else []

    # Mentors see only assigned villages
    if user_role == 'mentor':
        if hasattr(user, 'profile') and user.profile:
            assigned = user.profile.assigned_villages
            if hasattr(assigned, 'values_list'):
                return list(assigned.values_list('id', flat=True))
            return list(assigned) if assigned else []
        return []

    # Default: no access
    return []


def filter_queryset_by_village(queryset, user, village_field='village'):
    """
    Filter a queryset to only include records in user's accessible villages.

    Args:
        queryset: Django QuerySet
        user: User object
        village_field: Name of the village foreign key field

    Returns:
        Filtered QuerySet
    """
    village_ids = get_user_accessible_villages(user)

    if village_ids is None:
        # Unrestricted access
        return queryset

    if not village_ids:
        # No villages accessible
        return queryset.none()

    filter_kwargs = {f'{village_field}__in': village_ids}
    return queryset.filter(**filter_kwargs)


# =============================================================================
# Permission Decorators
# =============================================================================

def module_permission_required(module, level='read', json_response=False):
    """
    Decorator to check module-level permissions.
    Supports both built-in roles and custom roles.

    Args:
        module: Module key (e.g., 'households', 'grants')
        level: 'read' or 'full'
        json_response: Return JSON error instead of redirect

    Usage:
        @module_permission_required('households', 'read')
        def household_list(request):
            ...

        @module_permission_required('grants', 'full')
        def grant_approve(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not has_module_access(request.user, module, level):
                if json_response:
                    return JsonResponse({
                        'success': False,
                        'error': f'Permission denied. {level.title()} access to {module} required.'
                    }, status=403)
                else:
                    messages.error(request, f'You do not have permission to access {module}.')
                    return redirect('dashboard:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def read_permission_required(module):
    """Shortcut for read-only permission requirement."""
    return module_permission_required(module, 'read')


def write_permission_required(module):
    """Shortcut for write (full) permission requirement."""
    return module_permission_required(module, 'full')


def admin_or_custom_role_required(allowed_modules=None):
    """
    Decorator for views accessible by admins or users with custom roles
    that have access to specified modules.

    Args:
        allowed_modules: List of module keys. User needs access to at least one.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user has admin role
            if getattr(user, 'role', None) in ['ict_admin', 'program_manager']:
                return view_func(request, *args, **kwargs)

            # Check if user has custom role with access to any allowed module
            if allowed_modules:
                for module in allowed_modules:
                    if has_module_access(user, module, 'read'):
                        return view_func(request, *args, **kwargs)

            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:dashboard')
        return wrapper
    return decorator


# =============================================================================
# Context Processor for Templates
# =============================================================================

def permissions_context(request):
    """
    Add permission information to template context.
    Use in templates: {% if perms.can_edit_households %}
    """
    if not request.user.is_authenticated:
        return {'user_permissions': {}}

    user = request.user

    permissions = {
        'is_admin': user.is_superuser or getattr(user, 'role', None) in ['ict_admin', 'program_manager'],
        'can_view_dashboard': can_access_module(user, 'dashboard'),
        'can_view_households': can_access_module(user, 'households'),
        'can_edit_households': can_edit_module(user, 'households'),
        'can_view_programs': can_access_module(user, 'programs'),
        'can_edit_programs': can_edit_module(user, 'programs'),
        'can_view_business_groups': can_access_module(user, 'business_groups'),
        'can_edit_business_groups': can_edit_module(user, 'business_groups'),
        'can_view_savings_groups': can_access_module(user, 'savings_groups'),
        'can_edit_savings_groups': can_edit_module(user, 'savings_groups'),
        'can_view_training': can_access_module(user, 'training'),
        'can_edit_training': can_edit_module(user, 'training'),
        'can_view_grants': can_access_module(user, 'grants'),
        'can_edit_grants': can_edit_module(user, 'grants'),
        'can_view_reports': can_access_module(user, 'reports'),
        'can_view_settings': can_access_module(user, 'settings'),
        'can_edit_settings': can_edit_module(user, 'settings'),
        'can_manage_users': can_edit_module(user, 'users'),
        'can_view_audit_logs': can_access_module(user, 'audit_logs'),
    }

    return {'user_permissions': permissions}


# =============================================================================
# Helper Functions for Views
# =============================================================================

def check_access_or_403(user, module, level='read'):
    """
    Check access and raise HttpResponseForbidden if denied.
    Use in function-based views.
    """
    if not has_module_access(user, module, level):
        return HttpResponseForbidden(f'Permission denied. {level.title()} access to {module} required.')
    return None


def get_filtered_households(user):
    """
    Get households queryset filtered by user's accessible villages.
    """
    from households.models import Household
    queryset = Household.objects.all()
    return filter_queryset_by_village(queryset, user, 'village')


def get_filtered_business_groups(user):
    """
    Get business groups queryset filtered by user's accessible villages.
    """
    from business_groups.models import BusinessGroup
    queryset = BusinessGroup.objects.all()
    # BusinessGroup has members linked to households which have villages
    village_ids = get_user_accessible_villages(user)
    if village_ids is None:
        return queryset
    if not village_ids:
        return queryset.none()
    return queryset.filter(members__household__village_id__in=village_ids).distinct()


def get_filtered_savings_groups(user):
    """
    Get savings groups queryset filtered by user's accessible villages.
    """
    from savings_groups.models import BusinessSavingsGroup
    queryset = BusinessSavingsGroup.objects.all()
    village_ids = get_user_accessible_villages(user)
    if village_ids is None:
        return queryset
    if not village_ids:
        return queryset.none()
    return queryset.filter(members__household__village_id__in=village_ids).distinct()
