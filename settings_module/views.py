from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)

from .models import SystemConfiguration, UserSettings, SystemAuditLog, SystemAlert, UserAlertDismissal, SystemBackup

User = get_user_model()

@login_required
def settings_dashboard(request):
    """System settings dashboard"""
    # Check permissions
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'me_staff']):
        return HttpResponseForbidden("You do not have permission to access system settings.")

    # Get system statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users

    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_logins = SystemAuditLog.objects.filter(
        action='login',
        timestamp__gte=week_ago
    ).count()

    # System alerts
    active_alerts = SystemAlert.objects.filter(
        is_active=True,
        show_until__gt=timezone.now()
    ).count()

    # Configuration count
    config_count = SystemConfiguration.objects.count()

    # Last backup and backup count
    last_backup = SystemBackup.objects.filter(status='completed').order_by('-completed_at').first()
    backup_count = SystemBackup.objects.filter(status='completed').count()

    context = {
        'page_title': 'System Settings',
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'recent_logins': recent_logins,
        'active_alerts': active_alerts,
        'config_count': config_count,
        'last_backup': last_backup,
        'backup_count': backup_count,
        'system_version': '1.0.0',
    }
    return render(request, 'settings_module/settings_dashboard.html', context)

@login_required
def user_management(request):
    """User management page"""
    # Check permissions - only ICT admin and superuser can manage users
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('settings:settings_dashboard')

    users = User.objects.all().select_related('profile__supervisor').prefetch_related('profile__assigned_villages', 'supervised_profiles').order_by('-date_joined')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            username__icontains=search_query
        ) | users.filter(
            email__icontains=search_query
        ) | users.filter(
            first_name__icontains=search_query
        ) | users.filter(
            last_name__icontains=search_query
        )

    # Filter by role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)

    # Calculate role distribution before pagination
    all_users = User.objects.all()
    role_distribution = []
    for value, label in User.ROLE_CHOICES:
        count = all_users.filter(role=value).count()
        role_distribution.append({
            'value': value,
            'label': label,
            'count': count
        })

    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    context = {
        'page_title': 'User Management',
        'users': users,
        'role_choices': User.ROLE_CHOICES,
        'role_distribution': role_distribution,
        'search_query': search_query,
        'selected_role': role_filter,
    }
    return render(request, 'settings_module/user_management.html', context)

@login_required
def user_create(request):
    """Create new user"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to create users.')
        return redirect('settings:user_management')

    from .models import CustomRole

    # Get active custom roles
    custom_roles = CustomRole.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        password = request.POST.get('password')
        custom_role_id = request.POST.get('custom_role')

        if username and email and password:
            try:
                # Get custom role if specified
                custom_role = None
                if role == 'custom' and custom_role_id:
                    custom_role = CustomRole.objects.get(id=custom_role_id)

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role=role,
                    custom_role=custom_role
                )

                # Ensure UserProfile is created (signal should handle this, but explicit is safer)
                from accounts.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=user)

                # If using custom role with village restrictions, assign villages to profile
                if custom_role and custom_role.geographic_scope == 'villages':
                    profile.assigned_villages.set(custom_role.allowed_villages.all())

                messages.success(request, f'User "{username}" created successfully!')
                return redirect('settings:user_management')
            except CustomRole.DoesNotExist:
                messages.error(request, 'Selected custom role does not exist.')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Username, email, and password are required.')

    context = {
        'page_title': 'Create New User',
        'role_choices': User.ROLE_CHOICES,
        'custom_roles': custom_roles,
    }
    return render(request, 'settings_module/user_create.html', context)

@login_required
def user_edit(request, user_id):
    """Edit user"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to edit users.')
        return redirect('settings:user_management')

    from accounts.models import UserProfile
    from core.models import Village

    user = get_object_or_404(User, id=user_id)

    # Get or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.role = request.POST.get('role', user.role)

        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)

        try:
            user.save()

            # Handle supervisor assignment (for mentors)
            if user.role == 'mentor':
                supervisor_id = request.POST.get('supervisor')
                if supervisor_id:
                    try:
                        supervisor = User.objects.get(id=supervisor_id, role='field_associate')
                        user_profile.supervisor = supervisor
                    except User.DoesNotExist:
                        user_profile.supervisor = None
                else:
                    user_profile.supervisor = None
            else:
                user_profile.supervisor = None

            # Handle supervised mentors assignment (for field associates)
            if user.role == 'field_associate':
                mentor_ids = request.POST.getlist('supervised_mentors')
                logger.warning(f"FA UPDATE: User {user.username}, Mentor IDs from POST: {mentor_ids}")

                # Clear existing supervised mentors for this FA
                UserProfile.objects.filter(supervisor=user).update(supervisor=None)

                # Assign selected mentors to this FA
                if mentor_ids:
                    assigned_count = 0
                    for mentor_id in mentor_ids:
                        try:
                            mentor = User.objects.get(id=mentor_id, role='mentor')
                            mentor_profile, _ = UserProfile.objects.get_or_create(user=mentor)
                            mentor_profile.supervisor = user
                            mentor_profile.save()
                            assigned_count += 1
                        except User.DoesNotExist:
                            logger.warning(f"FA UPDATE: Mentor ID {mentor_id} not found")
                    logger.warning(f"FA UPDATE: Total {assigned_count} mentors assigned to {user.username}")
                else:
                    logger.warning(f"FA UPDATE: No mentors in POST for {user.username}, all cleared")

            # Handle village assignments (for mentors and field associates)
            if user.role in ['mentor', 'field_associate']:
                village_ids = request.POST.getlist('assigned_villages')
                logger.warning(f"VILLAGE UPDATE: User {user.username}, Role: {user.role}, Village IDs: {village_ids}")
                if village_ids:
                    villages = Village.objects.filter(id__in=village_ids)
                    user_profile.assigned_villages.set(villages)
                    logger.warning(f"VILLAGE UPDATE: Set {villages.count()} villages for {user.username}")
                else:
                    # Don't clear if no villages submitted - might be hidden form field
                    logger.warning(f"VILLAGE UPDATE: No villages in POST for {user.username}, keeping existing")
            # Only clear villages if role changes away from mentor/field_associate
            elif user_profile.assigned_villages.exists():
                logger.warning(f"VILLAGE UPDATE: Role changed to {user.role}, clearing villages for {user.username}")
                user_profile.assigned_villages.clear()

            user_profile.save()

            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('settings:user_management')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')

    # Get field associates for supervisor dropdown
    field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')

    # Get all mentors for FA assignment
    all_mentors = User.objects.filter(role='mentor', is_active=True).select_related('profile').prefetch_related('profile__assigned_villages').order_by('first_name', 'last_name')

    # Get currently supervised mentor IDs (for FA editing)
    supervised_mentor_ids = []
    supervised_mentors_list = []
    if user.role == 'field_associate':
        supervised_mentors_list = list(User.objects.filter(role='mentor', profile__supervisor=user))
        supervised_mentor_ids = [m.id for m in supervised_mentors_list]

    # Get all villages for assignment
    villages = Village.objects.all().select_related('subcounty_obj').order_by('subcounty_obj__name', 'name')

    # Get currently assigned village IDs
    assigned_village_ids = list(user_profile.assigned_villages.values_list('id', flat=True))

    context = {
        'page_title': f'Edit User - {user.username}',
        'user_obj': user,
        'user_profile': user_profile,
        'role_choices': User.ROLE_CHOICES,
        'field_associates': field_associates,
        'all_mentors': all_mentors,
        'supervised_mentor_ids': supervised_mentor_ids,
        'supervised_mentors_list': supervised_mentors_list,
        'supervised_mentors_count': len(supervised_mentors_list),
        'villages': villages,
        'assigned_village_ids': assigned_village_ids,
    }
    return render(request, 'settings_module/user_edit.html', context)

@login_required
@require_POST
def user_toggle_status(request, user_id):
    """Toggle user active status"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    user = get_object_or_404(User, id=user_id)

    # Don't allow deactivating superusers unless request user is also superuser
    if user.is_superuser and not request.user.is_superuser:
        return JsonResponse({'error': 'Cannot modify superuser status'}, status=403)

    # Don't allow users to deactivate themselves
    if user == request.user:
        return JsonResponse({'error': 'Cannot modify your own status'}, status=403)

    user.is_active = not user.is_active
    user.save()

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" has been {status}.')

    return JsonResponse({
        'success': True,
        'status': user.is_active,
        'message': f'User {status} successfully'
    })

@login_required
def user_delete(request, user_id):
    """Delete user"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to delete users.')
        return redirect('settings:user_management')

    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('settings:user_management')

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You cannot delete superuser accounts.')
        return redirect('settings:user_management')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted.')
        return redirect('settings:user_management')

    context = {
        'page_title': f'Delete User - {user.username}',
        'user_obj': user,
    }
    return render(request, 'settings_module/user_delete.html', context)


# System Configuration Views
@login_required
def system_config(request):
    """System configuration management"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("You do not have permission to access system configuration.")

    configs = SystemConfiguration.objects.all().order_by('category', 'key')

    # Group configurations by category
    config_groups = {}
    for config in configs:
        if config.category not in config_groups:
            config_groups[config.category] = []
        config_groups[config.category].append(config)

    context = {
        'page_title': 'System Configuration',
        'config_groups': config_groups,
        'total_configs': configs.count(),
    }
    return render(request, 'settings_module/system_config.html', context)


@login_required
def config_edit(request, config_id):
    """Edit system configuration"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("Permission denied.")

    config = get_object_or_404(SystemConfiguration, id=config_id)

    if not config.is_editable:
        messages.error(request, 'This configuration setting cannot be modified.')
        return redirect('settings:system_config')

    if request.method == 'POST':
        old_value = config.value
        config.value = request.POST.get('value', config.value)
        config.modified_by = request.user

        try:
            config.save()

            # Log the change
            SystemAuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='SystemConfiguration',
                object_id=str(config.id),
                object_repr=str(config),
                changes={'old_value': old_value, 'new_value': config.value},
                success=True
            )

            messages.success(request, f'Configuration "{config.key}" updated successfully!')
            return redirect('settings:system_config')
        except Exception as e:
            messages.error(request, f'Error updating configuration: {str(e)}')

    context = {
        'page_title': f'Edit Configuration - {config.key}',
        'config': config,
    }
    return render(request, 'settings_module/config_edit.html', context)


# User Profile Management
@login_required
def user_settings(request, user_id=None):
    """View/edit user settings"""
    if user_id:
        # Admin viewing/editing another user's settings
        if not (request.user.is_superuser or request.user.role == 'ict_admin'):
            return HttpResponseForbidden("Permission denied.")
        user = get_object_or_404(User, id=user_id)
    else:
        # User viewing/editing their own settings
        user = request.user

    settings_obj, created = UserSettings.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update profile picture if uploaded
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            try:
                user.save()
                messages.success(request, 'Profile picture updated successfully!')
            except Exception as e:
                messages.error(request, f'Error uploading profile picture: {str(e)}')

        # Update settings
        settings_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        settings_obj.sms_notifications = request.POST.get('sms_notifications') == 'on'
        settings_obj.theme = request.POST.get('theme', settings_obj.theme)
        settings_obj.language = request.POST.get('language', settings_obj.language)
        settings_obj.timezone = request.POST.get('timezone', settings_obj.timezone)

        try:
            settings_obj.save()
            messages.success(request, 'Settings updated successfully!')

            # Log the change
            SystemAuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='UserSettings',
                object_id=str(settings_obj.id),
                object_repr=str(settings_obj),
                success=True
            )

        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')

    context = {
        'page_title': f'User Settings - {user.get_full_name() or user.username}',
        'settings_user': user,
        'settings_obj': settings_obj,
        'is_own_settings': user == request.user,
    }
    return render(request, 'settings_module/user_settings.html', context)


# Audit Log Views
@login_required
def audit_logs(request):
    """View system audit logs"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'me_staff']):
        return HttpResponseForbidden("You do not have permission to view audit logs.")

    logs = SystemAuditLog.objects.all().select_related('user').order_by('-timestamp')

    # Custom search query - searches across multiple fields
    search_query = request.GET.get('q')
    if search_query:
        logs = logs.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(model_name__icontains=search_query) |
            Q(object_repr__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(request_path__icontains=search_query) |
            Q(error_message__icontains=search_query)
        )

    # Filters
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)

    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)

    model_filter = request.GET.get('model')
    if model_filter:
        logs = logs.filter(model_name__icontains=model_filter)

    # IP address filter
    ip_filter = request.GET.get('ip')
    if ip_filter:
        logs = logs.filter(ip_address__icontains=ip_filter)

    date_from = request.GET.get('date_from')
    if date_from:
        try:
            from datetime import datetime
            # Parse date string and create datetime at start of day
            dt_from = datetime.strptime(date_from, '%Y-%m-%d')
            # Make timezone aware
            dt_from = timezone.make_aware(dt_from, timezone.get_current_timezone())
            logs = logs.filter(timestamp__gte=dt_from)
        except (ValueError, TypeError):
            pass  # Invalid date format, skip filter

    date_to = request.GET.get('date_to')
    if date_to:
        try:
            from datetime import datetime, timedelta
            # Parse date string and create datetime at end of day
            dt_to = datetime.strptime(date_to, '%Y-%m-%d')
            dt_to = dt_to + timedelta(days=1)  # Include the entire day
            # Make timezone aware
            dt_to = timezone.make_aware(dt_to, timezone.get_current_timezone())
            logs = logs.filter(timestamp__lt=dt_to)
        except (ValueError, TypeError):
            pass  # Invalid date format, skip filter

    # Success/failure filter
    success_filter = request.GET.get('success')
    if success_filter == 'true':
        logs = logs.filter(success=True)
    elif success_filter == 'false':
        logs = logs.filter(success=False)

    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)

    context = {
        'page_title': 'System Audit Logs',
        'logs': logs,
        'action_choices': SystemAuditLog.ACTION_TYPES,
        'filters': {
            'q': search_query,
            'action': action_filter,
            'user': user_filter,
            'model': model_filter,
            'ip': ip_filter,
            'date_from': date_from,
            'date_to': date_to,
            'success': success_filter,
        },
    }
    return render(request, 'settings_module/audit_logs.html', context)


# System Alerts Management
@login_required
def system_alerts(request):
    """Manage system alerts"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("Permission denied.")

    alerts = SystemAlert.objects.all().order_by('-created_at')

    context = {
        'page_title': 'System Alerts',
        'alerts': alerts,
    }
    return render(request, 'settings_module/system_alerts.html', context)


@login_required
def create_alert(request):
    """Create system alert"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return HttpResponseForbidden("Permission denied.")

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        alert_type = request.POST.get('alert_type', 'info')
        scope = request.POST.get('scope', 'system')

        if title and message:
            alert = SystemAlert.objects.create(
                title=title,
                message=message,
                alert_type=alert_type,
                scope=scope,
                created_by=request.user
            )

            # Handle role targeting if scope is 'role'
            if scope == 'role':
                target_roles = request.POST.getlist('target_roles')
                alert.target_roles = target_roles
                alert.save()

            messages.success(request, 'System alert created successfully!')
            return redirect('settings:system_alerts')
        else:
            messages.error(request, 'Title and message are required.')

    context = {
        'page_title': 'Create System Alert',
        'alert_types': SystemAlert.ALERT_TYPES,
        'alert_scopes': SystemAlert.ALERT_SCOPES,
        'role_choices': User.ROLE_CHOICES,
    }
    return render(request, 'settings_module/create_alert.html', context)


@login_required
def toggle_alert(request, alert_id):
    """Toggle alert active status"""
    from django.http import JsonResponse

    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    alert = get_object_or_404(SystemAlert, id=alert_id)

    if request.method == 'POST':
        try:
            activate = request.POST.get('activate', 'false') == 'true'
            alert.is_active = activate
            alert.save()

            action = 'activated' if activate else 'deactivated'
            return JsonResponse({
                'success': True,
                'message': f'Alert "{alert.title}" has been {action}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_alert(request, alert_id):
    """Delete a system alert"""
    from django.http import JsonResponse

    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    alert = get_object_or_404(SystemAlert, id=alert_id)

    if request.method == 'POST':
        try:
            alert_title = alert.title
            alert.delete()

            return JsonResponse({
                'success': True,
                'message': f'Alert "{alert_title}" has been deleted'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def kobo_settings(request):
    """KoboToolbox API configuration settings"""
    # Check permissions - only ICT admin and superuser
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to manage KoboToolbox settings.')
        return redirect('settings:settings_dashboard')

    # Define Kobo configuration keys
    kobo_configs = {
        'kobo_api_url': {
            'key': 'kobo_api_url',
            'default': 'https://kf.kobotoolbox.org/api/v2',
            'description': 'KoboToolbox API URL',
            'category': 'kobo',
            'setting_type': 'string',
        },
        'kobo_api_token': {
            'key': 'kobo_api_token',
            'default': '',
            'description': 'KoboToolbox API Token (from Account Settings)',
            'category': 'kobo',
            'setting_type': 'string',
        },
        'kobo_webhook_secret': {
            'key': 'kobo_webhook_secret',
            'default': '',
            'description': 'Webhook Secret Key (optional)',
            'category': 'kobo',
            'setting_type': 'string',
        },
        'kobo_auto_sync_on_activation': {
            'key': 'kobo_auto_sync_on_activation',
            'default': 'true',
            'description': 'Auto-sync forms when activated',
            'category': 'kobo',
            'setting_type': 'boolean',
        },
        'kobo_allow_new_households': {
            'key': 'kobo_allow_new_households',
            'default': 'true',
            'description': 'Allow creating new households from Kobo submissions',
            'category': 'kobo',
            'setting_type': 'boolean',
        },
    }

    if request.method == 'POST':
        try:
            # Update or create configuration values
            for config_key, config_data in kobo_configs.items():
                value = request.POST.get(config_key, config_data['default'])

                config, created = SystemConfiguration.objects.get_or_create(
                    key=config_key,
                    defaults={
                        'value': value,
                        'setting_type': config_data['setting_type'],
                        'description': config_data['description'],
                        'category': config_data['category'],
                        'created_by': request.user,
                    }
                )

                if not created:
                    config.value = value
                    config.modified_by = request.user
                    config.save()

            messages.success(request, 'KoboToolbox settings updated successfully!')
            return redirect('settings:kobo_settings')

        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')

    # Get current configuration values
    current_config = {}
    for config_key, config_data in kobo_configs.items():
        try:
            config = SystemConfiguration.objects.get(key=config_key)
            current_config[config_key] = config.value
        except SystemConfiguration.DoesNotExist:
            current_config[config_key] = config_data['default']

    context = {
        'page_title': 'KoboToolbox Settings',
        'kobo_configs': kobo_configs,
        'current_config': current_config,
    }

    return render(request, 'settings_module/kobo_settings.html', context)


@login_required
def kobo_test_connection(request):
    """Test KoboToolbox API connection"""
    import requests

    # Check permissions
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to test Kobo connection.'
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    try:
        # Get API settings from request or database
        data = json.loads(request.body) if request.body else {}
        api_url = data.get('api_url')
        api_token = data.get('api_token')

        # If not provided in request, get from database
        if not api_url or not api_token:
            try:
                from .models import SystemConfiguration
                if not api_url:
                    config = SystemConfiguration.objects.get(key='kobo_api_url')
                    api_url = config.value
            except SystemConfiguration.DoesNotExist:
                api_url = 'https://kf.kobotoolbox.org/api/v2'

            if not api_token:
                try:
                    config = SystemConfiguration.objects.get(key='kobo_api_token')
                    api_token = config.value
                except SystemConfiguration.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'API token not configured. Please enter your API token first.'
                    })

        if not api_token:
            return JsonResponse({
                'success': False,
                'message': 'API token is required to test the connection.'
            })

        # Test the connection by fetching user info
        headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json',
        }

        # Try to get the user profile (lightweight endpoint)
        test_url = f"{api_url}/assets/"
        response = requests.get(test_url, headers=headers, timeout=15, params={'limit': 1})

        if response.status_code == 200:
            data = response.json()
            asset_count = data.get('count', 0)
            return JsonResponse({
                'success': True,
                'message': f'Connection successful! Found {asset_count} forms in your KoboToolbox account.',
                'details': {
                    'asset_count': asset_count,
                    'api_url': api_url,
                }
            })
        elif response.status_code == 401:
            return JsonResponse({
                'success': False,
                'message': 'Authentication failed. Please check your API token is correct.'
            })
        elif response.status_code == 403:
            return JsonResponse({
                'success': False,
                'message': 'Access denied. Your API token may not have the required permissions.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Connection failed with status code {response.status_code}. Please check your API URL.'
            })

    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'message': 'Connection timed out. KoboToolbox server may be slow or unreachable.'
        })
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'success': False,
            'message': 'Could not connect to KoboToolbox. Please check your internet connection and API URL.'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error testing connection: {str(e)}'
        }, status=500)


# =============================================================================
# Custom Role Management Views
# =============================================================================

@login_required
def custom_role_list(request):
    """List all custom roles"""
    # Check permissions - only ICT admin and superuser can manage roles
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to manage custom roles.')
        return redirect('settings:settings_dashboard')

    from .models import CustomRole

    roles = CustomRole.objects.all().annotate(
        user_count=Count('users')
    ).order_by('name')

    # Get available modules for reference
    available_modules = CustomRole.get_available_modules()

    context = {
        'page_title': 'Custom Roles',
        'roles': roles,
        'available_modules': available_modules,
    }
    return render(request, 'settings_module/custom_role_list.html', context)


@login_required
def custom_role_create(request):
    """Create a new custom role"""
    # Check permissions
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to create custom roles.')
        return redirect('settings:custom_role_list')

    from .models import CustomRole
    from core.models import Village, SubCounty, County

    available_modules = CustomRole.get_available_modules()

    # Get geographic data - use proper field paths through related models
    villages = Village.objects.select_related('subcounty_obj', 'subcounty_obj__county').all().order_by('subcounty_obj__name', 'name')
    counties = list(County.objects.values_list('name', flat=True).distinct().order_by('name'))
    subcounties = list(SubCounty.objects.values_list('name', flat=True).distinct().order_by('name'))

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        dashboard_type = request.POST.get('dashboard_type', 'general')
        is_active = request.POST.get('is_active') == 'on'

        # Geographic data
        geographic_scope = request.POST.get('geographic_scope', 'all')
        allowed_county = request.POST.get('allowed_county', '')
        allowed_subcounties = request.POST.getlist('allowed_subcounties')
        allowed_village_ids = request.POST.getlist('allowed_villages')

        # Validate name
        if not name:
            messages.error(request, 'Role name is required.')
        elif CustomRole.objects.filter(name__iexact=name).exists():
            messages.error(request, f'A role with the name "{name}" already exists.')
        else:
            # Build permissions from form data
            permissions = {}
            for module_key in available_modules.keys():
                permission_level = request.POST.get(f'permission_{module_key}', 'none')
                permissions[module_key] = permission_level

            try:
                role = CustomRole.objects.create(
                    name=name,
                    description=description,
                    dashboard_type=dashboard_type,
                    is_active=is_active,
                    permissions=permissions,
                    geographic_scope=geographic_scope,
                    allowed_county=allowed_county if geographic_scope == 'county' else '',
                    allowed_subcounties=allowed_subcounties if geographic_scope == 'subcounty' else [],
                    created_by=request.user,
                    updated_by=request.user,
                )

                # Add allowed villages if scope is 'villages'
                if geographic_scope == 'villages' and allowed_village_ids:
                    role.allowed_villages.set(allowed_village_ids)

                # Log the action
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='create',
                    model_name='CustomRole',
                    object_id=str(role.id),
                    object_repr=str(role),
                    success=True
                )

                messages.success(request, f'Custom role "{name}" created successfully!')
                return redirect('settings:custom_role_list')

            except Exception as e:
                messages.error(request, f'Error creating role: {str(e)}')

    context = {
        'page_title': 'Create Custom Role',
        'available_modules': available_modules,
        'dashboard_choices': [
            ('admin', 'Admin Dashboard'),
            ('executive', 'Executive Dashboard'),
            ('mentor', 'Mentor Dashboard'),
            ('me', 'M&E Dashboard'),
            ('field_associate', 'Field Associate Dashboard'),
            ('general', 'General Dashboard'),
        ],
        'villages': villages,
        'counties': counties,
        'subcounties': subcounties,
    }
    return render(request, 'settings_module/custom_role_form.html', context)


@login_required
def custom_role_edit(request, role_id):
    """Edit an existing custom role"""
    # Check permissions
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to edit custom roles.')
        return redirect('settings:custom_role_list')

    from .models import CustomRole
    from core.models import Village, SubCounty, County

    role = get_object_or_404(CustomRole, id=role_id)
    available_modules = CustomRole.get_available_modules()

    # Get geographic data - use proper field paths through related models
    villages = Village.objects.select_related('subcounty_obj', 'subcounty_obj__county').all().order_by('subcounty_obj__name', 'name')
    counties = list(County.objects.values_list('name', flat=True).distinct().order_by('name'))
    subcounties = list(SubCounty.objects.values_list('name', flat=True).distinct().order_by('name'))

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        dashboard_type = request.POST.get('dashboard_type', 'general')
        is_active = request.POST.get('is_active') == 'on'

        # Geographic data
        geographic_scope = request.POST.get('geographic_scope', 'all')
        allowed_county = request.POST.get('allowed_county', '')
        allowed_subcounties = request.POST.getlist('allowed_subcounties')
        allowed_village_ids = request.POST.getlist('allowed_villages')

        # Validate name
        if not name:
            messages.error(request, 'Role name is required.')
        elif CustomRole.objects.filter(name__iexact=name).exclude(id=role_id).exists():
            messages.error(request, f'A role with the name "{name}" already exists.')
        else:
            # Build permissions from form data
            permissions = {}
            for module_key in available_modules.keys():
                permission_level = request.POST.get(f'permission_{module_key}', 'none')
                permissions[module_key] = permission_level

            try:
                role.name = name
                role.description = description
                role.dashboard_type = dashboard_type
                role.is_active = is_active
                role.permissions = permissions
                role.geographic_scope = geographic_scope
                role.allowed_county = allowed_county if geographic_scope == 'county' else ''
                role.allowed_subcounties = allowed_subcounties if geographic_scope == 'subcounty' else []
                role.updated_by = request.user
                role.save()

                # Update allowed villages
                if geographic_scope == 'villages':
                    role.allowed_villages.set(allowed_village_ids)
                else:
                    role.allowed_villages.clear()

                # Log the action
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='CustomRole',
                    object_id=str(role.id),
                    object_repr=str(role),
                    changes={'permissions': permissions, 'geographic_scope': geographic_scope},
                    success=True
                )

                messages.success(request, f'Custom role "{name}" updated successfully!')
                return redirect('settings:custom_role_list')

            except Exception as e:
                messages.error(request, f'Error updating role: {str(e)}')

    context = {
        'page_title': f'Edit Custom Role - {role.name}',
        'role': role,
        'available_modules': available_modules,
        'dashboard_choices': [
            ('admin', 'Admin Dashboard'),
            ('executive', 'Executive Dashboard'),
            ('mentor', 'Mentor Dashboard'),
            ('me', 'M&E Dashboard'),
            ('field_associate', 'Field Associate Dashboard'),
            ('general', 'General Dashboard'),
        ],
        'villages': villages,
        'counties': counties,
        'subcounties': subcounties,
    }
    return render(request, 'settings_module/custom_role_form.html', context)


@login_required
def custom_role_delete(request, role_id):
    """Delete a custom role"""
    # Check permissions
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to delete custom roles.'
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    from .models import CustomRole

    role = get_object_or_404(CustomRole, id=role_id)

    # Check if any users are using this role
    user_count = User.objects.filter(custom_role=role).count()
    if user_count > 0:
        return JsonResponse({
            'success': False,
            'message': f'Cannot delete role "{role.name}". It is assigned to {user_count} user(s). Please reassign those users first.'
        })

    try:
        role_name = role.name
        role_id = role.id

        # Log the action before deletion
        SystemAuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='CustomRole',
            object_id=str(role_id),
            object_repr=role_name,
            success=True
        )

        role.delete()

        return JsonResponse({
            'success': True,
            'message': f'Custom role "{role_name}" deleted successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting role: {str(e)}'
        }, status=500)


@login_required
def custom_role_detail(request, role_id):
    """View details of a custom role (AJAX)"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)

    from .models import CustomRole

    role = get_object_or_404(CustomRole, id=role_id)
    available_modules = CustomRole.get_available_modules()

    # Build permissions list with module names
    permissions_list = []
    for module_key, module_name in available_modules.items():
        level = role.permissions.get(module_key, 'none')
        permissions_list.append({
            'module': module_name,
            'level': level,
            'level_display': {
                'full': 'Full Access',
                'read': 'Read Only',
                'none': 'No Access'
            }.get(level, 'No Access')
        })

    # Get users with this role
    users = User.objects.filter(custom_role=role).values('id', 'username', 'first_name', 'last_name', 'email')

    return JsonResponse({
        'success': True,
        'role': {
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'dashboard_type': role.get_dashboard_type_display(),
            'is_active': role.is_active,
            'created_by': role.created_by.get_full_name() if role.created_by else 'Unknown',
            'created_at': role.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': role.updated_at.strftime('%Y-%m-%d %H:%M'),
            'permissions': permissions_list,
            'users': list(users),
            'user_count': len(users),
        }
    })
