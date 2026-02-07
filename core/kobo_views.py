"""
KoBoToolbox Integration Views
Provides UI and API for exporting data and pushing to KoBoToolbox
"""

import io
import zipfile
import json
import requests
from datetime import date

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings

from .kobo_export import (
    export_households_csv,
    export_bm_cycles_csv,
    export_villages_csv,
    export_business_groups_csv,
    export_mentors_csv,
    export_all_reference_data
)
from .models import SystemSettings


def get_kobo_settings():
    """Get KoboToolbox settings from database (SystemConfiguration), falling back to Django settings"""
    try:
        from settings_module.models import SystemConfiguration

        def get_config(key, default=''):
            try:
                config = SystemConfiguration.objects.get(key=key)
                return config.value
            except SystemConfiguration.DoesNotExist:
                return default

        api_url = get_config('kobo_api_url', 'https://kf.kobotoolbox.org/api/v2')
        api_token = get_config('kobo_api_token', '')
        webhook_secret = get_config('kobo_webhook_secret', '')

        return {
            'api_url': api_url,
            'token': api_token,
            'base_url': api_url.replace('/api/v2', ''),
            'webhook_secret': webhook_secret,
            'enabled': True,
            'asset_uid': getattr(django_settings, 'KOBO_ASSET_UID', ''),
        }
    except Exception:
        # Fallback to Django settings if database not ready
        return {
            'api_url': getattr(django_settings, 'KOBO_API_URL', 'https://kf.kobotoolbox.org/api/v2'),
            'token': getattr(django_settings, 'KOBO_API_TOKEN', ''),
            'base_url': getattr(django_settings, 'KOBO_BASE_URL', 'https://kf.kobotoolbox.org'),
            'webhook_secret': '',
            'enabled': True,
            'asset_uid': getattr(django_settings, 'KOBO_ASSET_UID', ''),
        }


# Legacy variable for backward compatibility
KOBO_SETTINGS = get_kobo_settings()


@login_required
def kobo_export_dashboard(request):
    """Dashboard for KoBoToolbox exports"""
    from households.models import Household
    from core.models import BusinessMentorCycle, Village, Mentor
    from business_groups.models import BusinessGroup

    kobo_settings = get_kobo_settings()

    context = {
        'household_count': Household.objects.count(),
        'bm_cycle_count': BusinessMentorCycle.objects.count(),
        'village_count': Village.objects.count(),
        'business_group_count': BusinessGroup.objects.count(),
        'mentor_count': Mentor.objects.count(),
        'kobo_configured': bool(kobo_settings.get('token')),
        'kobo_enabled': kobo_settings.get('enabled', True),
    }

    return render(request, 'core/kobo_export_dashboard.html', context)


@login_required
def export_households(request):
    """Export households CSV for KoBoToolbox"""
    village = request.GET.get('village')
    status = request.GET.get('status')
    return export_households_csv(request, village=village, status=status)


@login_required
def export_bm_cycles(request):
    """Export BM Cycles CSV for KoBoToolbox"""
    return export_bm_cycles_csv(request)


@login_required
def export_villages(request):
    """Export villages CSV for KoBoToolbox"""
    county = request.GET.get('county')
    subcounty = request.GET.get('subcounty')
    return export_villages_csv(request, county=county, subcounty=subcounty)


@login_required
def export_business_groups(request):
    """Export business groups CSV for KoBoToolbox"""
    status = request.GET.get('status')
    return export_business_groups_csv(request, status=status)


@login_required
def export_mentors(request):
    """Export mentors CSV for KoBoToolbox"""
    return export_mentors_csv(request)


@login_required
def export_all_zip(request):
    """Export all reference data as a ZIP file"""
    exports = export_all_reference_data()

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in exports.items():
            zip_file.writestr(filename, content)

    # Return ZIP file
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="kobo_reference_data_{date.today().isoformat()}.zip"'
    return response


@login_required
def kobo_settings(request):
    """Manage KoBoToolbox API settings"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Only admins can access settings
    if not (user.is_superuser or user_role in ['ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to access system settings.')
        return redirect('dashboard:dashboard')

    # Get current settings from database
    settings_obj = SystemSettings.get_settings()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')

        if action == 'save':
            # Update settings
            settings_obj.kobo_api_url = request.POST.get('kobo_api_url', 'https://kf.kobotoolbox.org/api/v2')
            settings_obj.kobo_api_token = request.POST.get('kobo_api_token', '')
            settings_obj.kobo_base_url = request.POST.get('kobo_base_url', 'https://kf.kobotoolbox.org')
            settings_obj.kobo_webhook_secret = request.POST.get('kobo_webhook_secret', '')
            settings_obj.kobo_enabled = request.POST.get('kobo_enabled') == 'on'
            settings_obj.updated_by = user
            settings_obj.save()

            messages.success(request, 'KoboToolbox settings saved successfully!')
            return redirect('core:kobo_settings')

        elif action == 'test':
            # Test the API connection
            token = request.POST.get('kobo_api_token', settings_obj.kobo_api_token)
            api_url = request.POST.get('kobo_api_url', settings_obj.kobo_api_url)

            if not token:
                messages.error(request, 'Please enter an API token to test the connection.')
                return redirect('core:kobo_settings')

            try:
                headers = {'Authorization': f'Token {token}'}
                response = requests.get(f'{api_url}/assets/', headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    asset_count = data.get('count', 0)
                    messages.success(request, f'Connection successful! Found {asset_count} assets in your KoboToolbox account.')
                elif response.status_code == 401:
                    messages.error(request, 'Authentication failed. Please check your API token.')
                else:
                    messages.error(request, f'Connection failed with status {response.status_code}: {response.text[:200]}')

            except requests.Timeout:
                messages.error(request, 'Connection timed out. Please check the API URL.')
            except requests.RequestException as e:
                messages.error(request, f'Connection error: {str(e)}')

            return redirect('core:kobo_settings')

    # Get current settings for display
    current_settings = get_kobo_settings()

    context = {
        'page_title': 'KoboToolbox Settings',
        'settings_obj': settings_obj,
        'current_settings': {
            'api_url': settings_obj.kobo_api_url,
            'base_url': settings_obj.kobo_base_url,
            'token_configured': bool(settings_obj.kobo_api_token),
            'token': settings_obj.kobo_api_token,  # Show actual token for editing
            'webhook_secret': settings_obj.kobo_webhook_secret,
            'enabled': settings_obj.kobo_enabled,
        }
    }
    return render(request, 'core/kobo_settings.html', context)


@login_required
def push_to_kobo(request):
    """Push CSV files to KoBoToolbox via API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Get current settings from database
    kobo_settings = get_kobo_settings()

    if not kobo_settings.get('token'):
        return JsonResponse({
            'error': 'KoBoToolbox API token not configured. Go to Settings > KoboToolbox Settings to add your token.'
        }, status=400)

    if not kobo_settings.get('asset_uid'):
        return JsonResponse({
            'error': 'KoBoToolbox Asset UID not configured. Add KOBO_ASSET_UID to settings.py'
        }, status=400)

    export_type = request.POST.get('export_type', 'all')
    results = {}

    headers = {
        'Authorization': f"Token {kobo_settings['token']}"
    }

    # Map of export types to functions and filenames
    export_map = {
        'households': ('households.csv', export_households_csv),
        'bm_cycles': ('bm_cycles.csv', export_bm_cycles_csv),
        'villages': ('villages.csv', export_villages_csv),
        'business_groups': ('business_groups.csv', export_business_groups_csv),
        'mentors': ('mentors.csv', export_mentors_csv),
    }

    if export_type == 'all':
        exports_to_push = export_map.keys()
    else:
        exports_to_push = [export_type]

    for exp_type in exports_to_push:
        if exp_type not in export_map:
            continue

        filename, export_func = export_map[exp_type]
        csv_content = export_func()

        # Upload to KoBoToolbox
        try:
            files_url = f"{kobo_settings['api_url']}/assets/{kobo_settings['asset_uid']}/files/"

            # First, check if file exists and delete it
            existing_files_resp = requests.get(files_url, headers=headers)
            if existing_files_resp.status_code == 200:
                existing_files = existing_files_resp.json().get('results', [])
                for ef in existing_files:
                    if ef.get('metadata', {}).get('filename') == filename:
                        # Delete existing file
                        delete_url = f"{files_url}{ef['uid']}/"
                        requests.delete(delete_url, headers=headers)
                        break

            # Upload new file
            files = {
                'content': (filename, csv_content, 'text/csv'),
                'metadata': (None, json.dumps({'filename': filename}), 'application/json'),
            }
            response = requests.post(files_url, headers=headers, files=files)

            if response.status_code in [200, 201]:
                results[exp_type] = {'success': True, 'message': f'{filename} uploaded successfully'}
            else:
                results[exp_type] = {
                    'success': False,
                    'message': f'Failed to upload {filename}: {response.text}'
                }

        except requests.RequestException as e:
            results[exp_type] = {'success': False, 'message': f'Error: {str(e)}'}

    # Summary
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)

    return JsonResponse({
        'success': success_count == total_count,
        'message': f'{success_count}/{total_count} files uploaded successfully',
        'details': results
    })


# Management command helper for scheduled exports
def scheduled_kobo_push():
    """
    Function to be called by a scheduled task (cron/celery)
    Automatically pushes all reference data to KoBoToolbox
    """
    kobo_settings = get_kobo_settings()

    if not kobo_settings.get('token') or not kobo_settings.get('asset_uid'):
        return {'success': False, 'error': 'KoBoToolbox not configured'}

    headers = {
        'Authorization': f"Token {kobo_settings['token']}"
    }

    exports = export_all_reference_data()
    results = {}

    for filename, content in exports.items():
        try:
            files_url = f"{kobo_settings['api_url']}/assets/{kobo_settings['asset_uid']}/files/"
            files = {
                'content': (filename, content, 'text/csv'),
                'metadata': (None, json.dumps({'filename': filename}), 'application/json'),
            }
            response = requests.post(files_url, headers=headers, files=files)
            results[filename] = response.status_code in [200, 201]
        except Exception as e:
            results[filename] = False

    return results
