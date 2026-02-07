"""
Context processors for UPG System
"""

from core.permissions import can_access_module, can_edit_module, get_user_accessible_villages


def user_permissions(request):
    """
    Add user role and permission information to template context.
    Supports both built-in roles and custom roles.
    """
    # Safety check: ensure request.user exists (may not during error handling)
    if not hasattr(request, 'user'):
        return {}

    if request.user.is_authenticated:
        user = request.user
        user_role = getattr(user, 'role', None)

        # Check if user is executive (view-only role)
        is_executive = user_role in ['county_executive', 'county_assembly']

        # Check if user is Program Manager (supervises Field Associates)
        is_program_manager = user_role == 'program_manager'

        # Check if user has a custom role
        has_custom_role = user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role

        # Use centralized permission system for all checks
        # This now works for both built-in roles AND custom roles
        permissions = {
            # Module access permissions using centralized system
            'can_view_programs': can_access_module(user, 'programs'),
            'can_edit_programs': can_edit_module(user, 'programs'),

            'can_view_households': can_access_module(user, 'households'),
            'can_edit_households': can_edit_module(user, 'households'),

            'can_view_business_groups': can_access_module(user, 'business_groups'),
            'can_edit_business_groups': can_edit_module(user, 'business_groups'),

            'can_view_savings_groups': can_access_module(user, 'savings_groups'),
            'can_edit_savings_groups': can_edit_module(user, 'savings_groups'),

            'can_view_surveys': can_access_module(user, 'surveys'),
            'can_create_surveys': can_edit_module(user, 'surveys'),

            'can_view_training': can_access_module(user, 'training'),
            'can_create_training': can_edit_module(user, 'training'),
            'can_edit_training': can_edit_module(user, 'training'),
            'can_delete_training': can_edit_module(user, 'training'),
            'can_manage_training': can_edit_module(user, 'training'),

            'can_view_grants': can_access_module(user, 'grants'),
            'can_manage_grants': can_edit_module(user, 'grants'),

            'can_view_reports': can_access_module(user, 'reports'),
            'can_export_reports': can_access_module(user, 'reports'),

            'can_view_settings': can_access_module(user, 'settings'),
            'can_manage_users': can_edit_module(user, 'users'),

            # ESR Import permissions
            'can_import_esr': user.is_superuser or user_role == 'ict_admin',

            # BM Cycle permissions
            'can_manage_bm_cycles': can_access_module(user, 'training'),

            # Geographic restrictions
            'has_village_restrictions': get_user_accessible_villages(user) is not None,

            # Executive-specific flag for templates
            'is_view_only': is_executive,

            # PM-specific permissions
            'is_program_manager': is_program_manager,
            'can_manage_field_associates': user.is_superuser or user_role in ['ict_admin', 'program_manager'],
            'can_view_team_performance': user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff'],

            # Custom role indicator
            'has_custom_role': has_custom_role,
        }

        # Add user role information
        role_info = {
            'user_role': user.role,
            'user_role_display': user.get_role_display(),
            'is_mentor': user.role == 'mentor',
            'is_field_associate': user.role == 'field_associate',
            'is_program_manager': user.role == 'program_manager',
            'is_me_staff': user.role == 'me_staff',
            'is_ict_admin': user.role == 'ict_admin',
            'is_county_executive': user.role == 'county_executive',
            'is_county_assembly': user.role == 'county_assembly',
            'is_beneficiary': user.role == 'beneficiary',
        }

        # Village assignments for mentors and field associates
        village_info = {}
        if hasattr(user, 'profile') and user.profile and user.role in ['mentor', 'field_associate']:
            assigned_villages = user.profile.assigned_villages.all()
            village_info.update({
                'assigned_villages': assigned_villages,
                'assigned_villages_count': assigned_villages.count(),
                'has_village_assignments': assigned_villages.exists(),
            })

        return {
            'perms': permissions,
            'role_info': role_info,
            'village_info': village_info,
        }

    return {}


def system_alerts(request):
    """
    Add active system alerts to template context
    """
    # Safety check: ensure request.user exists (may not during error handling)
    if not hasattr(request, 'user'):
        return {}

    if request.user.is_authenticated:
        from settings_module.models import SystemAlert, UserAlertDismissal
        from django.utils import timezone

        # Get active alerts visible to this user
        active_alerts = SystemAlert.objects.filter(
            is_active=True,
            show_until__gt=timezone.now()
        )

        # Filter alerts by scope
        user_alerts = []
        for alert in active_alerts:
            if alert.is_visible_to_user(request.user):
                # Check if user has dismissed this alert
                dismissed = UserAlertDismissal.objects.filter(
                    user=request.user,
                    alert=alert
                ).exists()

                if not dismissed:
                    user_alerts.append(alert)

        return {
            'system_alerts': user_alerts,
            'alerts_count': len(user_alerts),
        }

    return {}