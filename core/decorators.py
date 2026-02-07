"""
Custom decorators for UPG System.
Provides reusable permission and validation decorators.
"""

from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(allowed_roles, redirect_url=None, json_response=False):
    """
    Decorator to restrict view access based on user roles.

    Args:
        allowed_roles: List of role strings that can access the view
        redirect_url: URL to redirect unauthorized users (default: dashboard)
        json_response: If True, return JSON error instead of redirect

    Usage:
        @role_required(['me_staff', 'ict_admin'])
        def admin_view(request):
            ...

        @role_required(['mentor', 'field_associate'], json_response=True)
        def api_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # Superusers always have access
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user has one of the allowed roles
            if hasattr(user, 'role') and user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Access denied
            if json_response:
                return JsonResponse({
                    'success': False,
                    'message': 'Permission denied. Required role: ' + ', '.join(allowed_roles)
                }, status=403)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url or 'dashboard:dashboard')

        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Shortcut decorator for views that require admin access.
    Equivalent to @role_required(['me_staff', 'ict_admin'])
    """
    return role_required(['me_staff', 'ict_admin'])(view_func)


def staff_required(view_func):
    """
    Shortcut decorator for views that require any staff role.
    """
    return role_required(['me_staff', 'ict_admin', 'mentor', 'field_associate', 'program_manager'])(view_func)


def mentor_required(view_func):
    """
    Shortcut decorator for views that require mentor access.
    """
    return role_required(['mentor', 'field_associate', 'me_staff', 'ict_admin'])(view_func)


def ajax_login_required(view_func):
    """
    Decorator for AJAX views that require authentication.
    Returns JSON response instead of redirect for unauthenticated requests.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_post_ajax(view_func):
    """
    Decorator that requires POST method and returns JSON response.
    Combines common AJAX view requirements.
    """
    @wraps(view_func)
    @ajax_login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'message': 'POST method required'
            }, status=405)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
