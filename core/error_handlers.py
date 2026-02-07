"""
Custom Error Handlers for UPG System

Provides user-friendly error pages and logging for production.
"""

import logging
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def handler400(request, exception=None):
    """Handle 400 Bad Request errors."""
    context = {
        'error_code': 400,
        'error_title': 'Bad Request',
        'error_message': 'The server could not understand your request. Please check your input and try again.',
        'suggestions': [
            'Check that all form fields are filled correctly',
            'Ensure you are submitting valid data',
            'Try refreshing the page and submitting again',
        ]
    }

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'error': True,
            'code': 400,
            'message': context['error_message']
        }, status=400)

    return render(request, 'errors/error.html', context, status=400)


def handler403(request, exception=None):
    """Handle 403 Forbidden errors."""
    context = {
        'error_code': 403,
        'error_title': 'Access Denied',
        'error_message': 'You do not have permission to access this resource.',
        'suggestions': [
            'Check that you are logged in with the correct account',
            'Contact your administrator if you believe you should have access',
            'Return to the dashboard and navigate from there',
        ]
    }

    # Log the access attempt
    logger.warning(
        f'403 Forbidden: User {request.user} attempted to access {request.path}',
        extra={'user': str(request.user), 'path': request.path}
    )

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'error': True,
            'code': 403,
            'message': context['error_message']
        }, status=403)

    return render(request, 'errors/error.html', context, status=403)


def handler404(request, exception=None):
    """Handle 404 Not Found errors."""
    context = {
        'error_code': 404,
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist or has been moved.',
        'suggestions': [
            'Check the URL for typos',
            'Use the navigation menu to find what you need',
            'Return to the dashboard',
        ]
    }

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'error': True,
            'code': 404,
            'message': context['error_message']
        }, status=404)

    return render(request, 'errors/error.html', context, status=404)


def handler500(request):
    """Handle 500 Internal Server Error."""
    # Log the error with full traceback
    error_id = None
    try:
        import uuid
        error_id = str(uuid.uuid4())[:8]
        logger.error(
            f'500 Internal Server Error (ID: {error_id}): {traceback.format_exc()}',
            extra={'error_id': error_id, 'path': request.path}
        )
    except Exception as log_error:
        logger.error(f'Error logging failed: {log_error}')

    context = {
        'error_code': 500,
        'error_title': 'Server Error',
        'error_message': 'Something went wrong on our end. We apologize for the inconvenience.',
        'error_id': error_id,
        'suggestions': [
            'Try refreshing the page',
            'Wait a few minutes and try again',
            'If the problem persists, contact support with error ID: ' + (error_id or 'N/A'),
        ],
        'show_contact': True
    }

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'error': True,
            'code': 500,
            'message': context['error_message'],
            'error_id': error_id
        }, status=500)

    return render(request, 'errors/error.html', context, status=500)


def handler503(request, exception=None):
    """Handle 503 Service Unavailable (maintenance mode)."""
    context = {
        'error_code': 503,
        'error_title': 'Service Unavailable',
        'error_message': 'The system is currently undergoing maintenance. Please check back shortly.',
        'suggestions': [
            'Wait a few minutes and try again',
            'Check the system status page for updates',
        ]
    }

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'error': True,
            'code': 503,
            'message': context['error_message']
        }, status=503)

    return render(request, 'errors/error.html', context, status=503)


# ============================================================================
# CSRF Error Handler
# ============================================================================

@csrf_exempt
def csrf_failure(request, reason=''):
    """Handle CSRF verification failures."""
    context = {
        'error_code': 403,
        'error_title': 'Session Expired',
        'error_message': 'Your session has expired or the security token is invalid. Please try again.',
        'suggestions': [
            'Refresh the page and try again',
            'Clear your browser cookies and log in again',
            'If the problem persists, contact support',
        ]
    }

    logger.warning(
        f'CSRF Failure: User {request.user} on {request.path}, Reason: {reason}',
        extra={'user': str(request.user), 'path': request.path, 'reason': reason}
    )

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'error': True,
            'code': 403,
            'message': 'CSRF verification failed. Please refresh and try again.'
        }, status=403)

    return render(request, 'errors/error.html', context, status=403)


# ============================================================================
# Exception Logging Middleware
# ============================================================================

class ErrorLoggingMiddleware:
    """
    Middleware to log all unhandled exceptions with context.
    Add to MIDDLEWARE in settings.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Log unhandled exceptions with request context."""
        import uuid
        error_id = str(uuid.uuid4())[:8]

        logger.error(
            f'Unhandled Exception (ID: {error_id})',
            exc_info=True,
            extra={
                'error_id': error_id,
                'path': request.path,
                'method': request.method,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')
            }
        )

        # Don't handle the exception - let Django's default handler take over
        return None

    def get_client_ip(self, request):
        """Get the client's IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'Unknown')


# ============================================================================
# API Error Response Helpers
# ============================================================================

def api_error_response(message, status_code=400, errors=None, error_id=None):
    """
    Create a standardized API error response.

    Usage:
        return api_error_response('Invalid data', 400, errors={'field': ['Error message']})
    """
    response_data = {
        'success': False,
        'error': True,
        'message': message,
        'status': status_code
    }

    if errors:
        response_data['errors'] = errors

    if error_id:
        response_data['error_id'] = error_id

    return JsonResponse(response_data, status=status_code)


def api_success_response(data=None, message='Success', status_code=200):
    """
    Create a standardized API success response.

    Usage:
        return api_success_response({'id': 1}, 'Created successfully', 201)
    """
    response_data = {
        'success': True,
        'message': message
    }

    if data is not None:
        response_data['data'] = data

    return JsonResponse(response_data, status=status_code)
