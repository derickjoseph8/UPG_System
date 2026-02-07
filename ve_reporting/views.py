"""
VE Reporting API Views for Django
Silent API module for Village Enterprise to fetch aggregated metrics.
No UI components - pure API access only.
"""
import json
from datetime import datetime
from functools import wraps
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from .models import VEApiKey
from .services import VEReportingService


def ve_api_key_required(view_func):
    """
    Decorator to verify VE API key from X-VE-API-Key header.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key_header = request.META.get('HTTP_X_VE_API_KEY')

        if not api_key_header:
            return JsonResponse({
                "error": "Missing X-VE-API-Key header"
            }, status=401)

        # Hash and lookup the key
        key_hash = VEApiKey.hash_key(api_key_header)
        try:
            api_key = VEApiKey.objects.get(
                key_hash=key_hash,
                is_deleted=False
            )
        except VEApiKey.DoesNotExist:
            return JsonResponse({
                "error": "Invalid API key"
            }, status=401)

        if not api_key.is_valid():
            return JsonResponse({
                "error": "API key is expired or revoked"
            }, status=401)

        # Record usage
        client_ip = get_client_ip(request)
        api_key.record_usage(client_ip)

        # Attach api_key to request for use in view
        request.ve_api_key = api_key

        return view_func(request, *args, **kwargs)

    return wrapper


def get_client_ip(request):
    """Get client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def add_cors_headers(response):
    """Add CORS headers to response for VE Data Hub access"""
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'X-VE-API-Key, Content-Type'
    return response


@method_decorator(csrf_exempt, name='dispatch')
class VEApiKeyRequiredMixin:
    """Mixin for class-based views requiring VE API key"""

    def dispatch(self, request, *args, **kwargs):
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            response = JsonResponse({})
            return add_cors_headers(response)

        api_key_header = request.META.get('HTTP_X_VE_API_KEY')

        if not api_key_header:
            response = JsonResponse({
                "error": "Missing X-VE-API-Key header"
            }, status=401)
            return add_cors_headers(response)

        key_hash = VEApiKey.hash_key(api_key_header)
        try:
            api_key = VEApiKey.objects.get(
                key_hash=key_hash,
                is_deleted=False
            )
        except VEApiKey.DoesNotExist:
            response = JsonResponse({
                "error": "Invalid API key"
            }, status=401)
            return add_cors_headers(response)

        if not api_key.is_valid():
            response = JsonResponse({
                "error": "API key is expired or revoked"
            }, status=401)
            return add_cors_headers(response)

        client_ip = get_client_ip(request)
        api_key.record_usage(client_ip)
        request.ve_api_key = api_key

        response = super().dispatch(request, *args, **kwargs)
        return add_cors_headers(response)


# ============ API Views ============

@method_decorator(csrf_exempt, name='dispatch')
class HealthView(VEApiKeyRequiredMixin, View):
    """Health check endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_health())


@method_decorator(csrf_exempt, name='dispatch')
class MetadataView(VEApiKeyRequiredMixin, View):
    """Instance metadata endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_metadata())


@method_decorator(csrf_exempt, name='dispatch')
class SummaryView(VEApiKeyRequiredMixin, View):
    """Overall summary metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_summary())


@method_decorator(csrf_exempt, name='dispatch')
class EnrollmentView(VEApiKeyRequiredMixin, View):
    """Enrollment metrics endpoint"""

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Parse dates if provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                start_date = None

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                end_date = None

        service = VEReportingService()
        return JsonResponse(service.get_enrollment(start_date, end_date))


@method_decorator(csrf_exempt, name='dispatch')
class BeneficiariesView(VEApiKeyRequiredMixin, View):
    """Beneficiary metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_beneficiaries())


@method_decorator(csrf_exempt, name='dispatch')
class GraduationView(VEApiKeyRequiredMixin, View):
    """Graduation metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_graduation())


@method_decorator(csrf_exempt, name='dispatch')
class SavingsView(VEApiKeyRequiredMixin, View):
    """Savings metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_savings())


@method_decorator(csrf_exempt, name='dispatch')
class TrainingView(VEApiKeyRequiredMixin, View):
    """Training metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_training())


@method_decorator(csrf_exempt, name='dispatch')
class DisbursementsView(VEApiKeyRequiredMixin, View):
    """Disbursement metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_disbursements())


@method_decorator(csrf_exempt, name='dispatch')
class MilestonesView(VEApiKeyRequiredMixin, View):
    """Milestone metrics endpoint"""

    def get(self, request):
        service = VEReportingService()
        return JsonResponse(service.get_milestones())


@method_decorator(csrf_exempt, name='dispatch')
class TimeSeriesView(VEApiKeyRequiredMixin, View):
    """Time series data endpoint"""

    def get(self, request):
        metric = request.GET.get('metric')
        interval = request.GET.get('interval', 'monthly')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not metric:
            return JsonResponse({
                "error": "Missing required parameter: metric"
            }, status=400)

        valid_metrics = ["enrollment", "graduation", "savings", "training", "disbursements"]
        if metric not in valid_metrics:
            return JsonResponse({
                "error": f"Invalid metric. Must be one of: {', '.join(valid_metrics)}"
            }, status=400)

        valid_intervals = ["daily", "weekly", "monthly"]
        if interval not in valid_intervals:
            return JsonResponse({
                "error": f"Invalid interval. Must be one of: {', '.join(valid_intervals)}"
            }, status=400)

        # Parse dates
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                start_date = None

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                end_date = None

        service = VEReportingService()
        return JsonResponse(service.get_timeseries(metric, interval, start_date, end_date))


# ============ Admin Views (For MIS Admins) ============

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


@csrf_exempt
@login_required
@user_passes_test(is_admin)
def create_api_key(request):
    """Create a new VE API key (admin only)"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = data.get('name')
    expires_in_days = data.get('expires_in_days')

    if not name:
        return JsonResponse({"error": "Name is required"}, status=400)

    # Generate key
    full_key, key_hash, key_prefix = VEApiKey.generate_key()

    # Calculate expiry
    expires_at = None
    if expires_in_days:
        from datetime import timedelta
        expires_at = timezone.now() + timedelta(days=int(expires_in_days))

    # Create key
    api_key = VEApiKey.objects.create(
        name=name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=["ve-reporting:read"],
        expires_at=expires_at,
        created_by=request.user
    )

    return JsonResponse({
        "id": str(api_key.uuid),
        "name": api_key.name,
        "key": full_key,  # Only shown on creation
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes,
        "is_active": api_key.is_active,
        "created_at": api_key.created_at.isoformat(),
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None
    })


@csrf_exempt
@login_required
@user_passes_test(is_admin)
def list_api_keys(request):
    """List all VE API keys (admin only)"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    keys = VEApiKey.objects.filter(is_deleted=False)

    return JsonResponse({
        "keys": [
            {
                "id": str(k.uuid),
                "name": k.name,
                "key_prefix": k.key_prefix,
                "scopes": k.scopes,
                "is_active": k.is_active,
                "created_at": k.created_at.isoformat(),
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None
            }
            for k in keys
        ]
    })


@csrf_exempt
@login_required
@user_passes_test(is_admin)
def revoke_api_key(request, key_id):
    """Revoke a VE API key (admin only)"""
    if request.method != 'DELETE':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        api_key = VEApiKey.objects.get(uuid=key_id, is_deleted=False)
    except VEApiKey.DoesNotExist:
        return JsonResponse({"error": "API key not found"}, status=404)

    reason = request.GET.get('reason', '')

    api_key.is_active = False
    api_key.revoked_at = timezone.now()
    api_key.revoked_by = request.user
    api_key.revoke_reason = reason
    api_key.save()

    return JsonResponse({"message": "API key revoked successfully"})


# ============ Web Views (For Settings Page) ============

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


@login_required
@user_passes_test(is_admin)
def ve_api_keys_list(request):
    """List all VE API keys (web view)"""
    api_keys = VEApiKey.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 've_reporting/api_keys.html', {
        'api_keys': api_keys
    })


@login_required
@user_passes_test(is_admin)
def ve_api_key_create_view(request):
    """Create a new VE API key (web view)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        expires_in_days = request.POST.get('expires_in_days')

        if not name:
            messages.error(request, 'Key name is required.')
            return render(request, 've_reporting/api_key_create.html')

        # Generate key
        full_key, key_hash, key_prefix = VEApiKey.generate_key()

        # Calculate expiry
        expires_at = None
        if expires_in_days:
            from datetime import timedelta
            expires_at = timezone.now() + timedelta(days=int(expires_in_days))

        # Create key
        api_key = VEApiKey.objects.create(
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix[:12],
            scopes=["ve-reporting:read"],
            expires_at=expires_at,
            created_by=request.user
        )

        messages.success(request, f'API Key "{name}" created successfully!')
        return render(request, 've_reporting/api_key_create.html', {
            'new_key': full_key,
            'key_name': name
        })

    return render(request, 've_reporting/api_key_create.html')


@login_required
@user_passes_test(is_admin)
def ve_api_key_revoke_view(request, key_id):
    """Revoke a VE API key (web view)"""
    api_key = get_object_or_404(VEApiKey, uuid=key_id, is_deleted=False)

    if request.method == 'POST':
        api_key.is_active = False
        api_key.revoked_at = timezone.now()
        api_key.revoked_by = request.user
        api_key.revoke_reason = 'Revoked via admin interface'
        api_key.save()
        messages.success(request, f'API Key "{api_key.name}" has been revoked.')

    return redirect('ve_reporting:ve_api_keys')
