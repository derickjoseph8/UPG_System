"""
Middleware for UPG System
"""

from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from settings_module.models import SystemAuditLog


def get_client_ip(request):
    """
    Get client IP address from request.
    Checks multiple headers for proxies/load balancers (AWS ELB, nginx, Cloudflare, etc.)
    """
    # List of headers to check, in order of preference
    ip_headers = [
        'HTTP_X_FORWARDED_FOR',      # Standard proxy header (AWS ELB, etc.)
        'HTTP_X_REAL_IP',            # Nginx proxy
        'HTTP_CF_CONNECTING_IP',     # Cloudflare
        'HTTP_TRUE_CLIENT_IP',       # Akamai, Cloudflare Enterprise
        'HTTP_X_CLIENT_IP',          # Some proxies
        'HTTP_X_CLUSTER_CLIENT_IP',  # Rackspace, Riverbed
        'REMOTE_ADDR',               # Direct connection (fallback)
    ]

    for header in ip_headers:
        ip = request.META.get(header)
        if ip:
            # X-Forwarded-For may contain multiple IPs: client, proxy1, proxy2
            # Take the first one (original client IP)
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            # Validate it's not a private/internal IP if we have more options
            if ip and ip not in ['127.0.0.1', 'localhost', '']:
                return ip

    # Fallback to REMOTE_ADDR even if it's localhost
    return request.META.get('REMOTE_ADDR', 'Unknown')


class AuditLogMiddleware:
    """
    Middleware to log user actions and system events
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request info for later use
        request.audit_data = {
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_path': request.path,
            'request_method': request.method,
        }

        response = self.get_response(request)

        # Log certain actions based on response status and path
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._log_action_if_needed(request, response)

        return response

    def _log_action_if_needed(self, request, response):
        """Log actions based on request path and method"""
        path = request.path
        method = request.method
        user = request.user

        # Skip certain paths
        skip_paths = ['/static/', '/media/', '/favicon.ico', '/admin/jsi18n/']
        if any(skip_path in path for skip_path in skip_paths):
            return

        # Log specific actions
        if method == 'POST' and response.status_code in [200, 201, 302]:
            action = 'create'
            model_name = ''
            object_repr = ''

            # Determine action and model based on path
            if '/create' in path or '/add' in path:
                action = 'create'
            elif '/edit' in path or '/update' in path:
                action = 'update'
            elif '/delete' in path:
                action = 'delete'
            elif 'login' in path:
                return  # Handled by signal
            elif 'logout' in path:
                return  # Handled by signal
            else:
                action = 'update'  # Generic POST action

            # Extract model name from URL
            url_parts = path.strip('/').split('/')
            if len(url_parts) > 0:
                model_name = url_parts[0].replace('-', '_').title()

            # Create audit log entry
            try:
                SystemAuditLog.objects.create(
                    user=user,
                    action=action,
                    model_name=model_name,
                    object_repr=object_repr,
                    ip_address=request.audit_data['ip_address'],
                    user_agent=request.audit_data['user_agent'],
                    request_path=request.audit_data['request_path'],
                    request_method=request.audit_data['request_method'],
                    success=True
                )
            except Exception:
                # Don't let audit logging break the application
                pass


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login events"""
    try:
        # Handle cases where request or request.method may be None (e.g., in tests)
        request_method = 'LOGIN'
        if request and hasattr(request, 'method') and request.method:
            request_method = request.method

        SystemAuditLog.objects.create(
            user=user,
            action='login',
            model_name='User',
            object_repr=str(user),
            ip_address=get_client_ip(request) if request else '',
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request and hasattr(request, 'META') else '',
            request_path=getattr(request, 'path', '/login/') if request else '/login/',
            request_method=request_method,
            success=True
        )
    except Exception:
        pass


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout events"""
    try:
        # Handle cases where request or request.method may be None (e.g., in tests)
        request_method = 'LOGOUT'
        if request and hasattr(request, 'method') and request.method:
            request_method = request.method

        SystemAuditLog.objects.create(
            user=user,
            action='logout',
            model_name='User',
            object_repr=str(user) if user else 'Anonymous',
            ip_address=get_client_ip(request) if request else '',
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request and hasattr(request, 'META') else '',
            request_path=getattr(request, 'path', '/logout/') if request else '/logout/',
            request_method=request_method,
            success=True
        )
    except Exception:
        pass