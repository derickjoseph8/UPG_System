from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from households.models import Household, HouseholdProgram, HouseholdMember, PPI
from business_groups.models import BusinessGroup, BusinessGroupMember
from upg_grants.models import SBGrant, PRGrant
from savings_groups.models import BusinessSavingsGroup, BSGMember
from training.models import Training, HouseholdTrainingEnrollment, MentoringVisit, PhoneNudge
from core.models import Village
import csv


def can_access_reports(user):
    """Check if user has permission to access reports module.
    Returns True if user can access, False otherwise.
    """
    if user.is_superuser:
        return True

    user_role = getattr(user, 'role', None)

    # Built-in roles with reports access
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly', 'field_associate', 'mentor']:
        return True

    # Check custom role permissions
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active:
            return custom_role.has_permission('reports', 'read')

    return False


def get_user_accessible_villages(user):
    """Get villages accessible to a user based on their role (built-in or custom).

    For custom roles, this respects geographic restrictions:
    - 'all': All villages
    - 'county': Villages in allowed county
    - 'subcounty': Villages in allowed subcounties
    - 'villages': Specifically assigned villages

    For built-in roles, uses profile's assigned_villages.

    Returns a queryset of Village objects or None for full access.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets full access
    if user.is_superuser:
        return None  # None means full access

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active:
            scope = custom_role.geographic_scope

            if scope == 'all':
                return None  # Full access

            elif scope == 'county' and custom_role.allowed_county:
                return Village.objects.filter(
                    subcounty_obj__county__name=custom_role.allowed_county
                )

            elif scope == 'subcounty' and custom_role.allowed_subcounties:
                return Village.objects.filter(
                    subcounty_obj__name__in=custom_role.allowed_subcounties
                )

            elif scope == 'villages':
                return custom_role.allowed_villages.all()

            return Village.objects.none()

    # For built-in roles, check profile's assigned villages
    if hasattr(user, 'profile') and user.profile:
        assigned = user.profile.assigned_villages.all()
        if assigned.exists():
            return assigned

    return None


def get_user_assigned_villages(user):
    """Get villages assigned to a user based on their role.
    Legacy function - now wraps get_user_accessible_villages for backward compatibility.
    """
    return get_user_accessible_villages(user)


def get_filtered_households(user):
    """Get households based on user role and assigned villages.
    Supports both built-in roles and custom roles with geographic restrictions.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets all
    if user.is_superuser:
        return Household.objects.all()

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active and custom_role.has_permission('households', 'read'):
            accessible_villages = get_user_accessible_villages(user)
            if accessible_villages is None:
                return Household.objects.all()
            return Household.objects.filter(village__in=accessible_villages)
        return Household.objects.none()

    # Built-in admin roles see all households
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return Household.objects.all()

    # FA and Mentor see only households in their assigned villages
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None:
            return Household.objects.filter(village__in=assigned_villages)
        return Household.objects.none()

    return Household.objects.none()


def get_filtered_business_groups(user):
    """Get business groups based on user role and assigned villages.
    Supports both built-in roles and custom roles with geographic restrictions.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets all
    if user.is_superuser:
        return BusinessGroup.objects.all()

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active and custom_role.has_permission('business_groups', 'read'):
            accessible_villages = get_user_accessible_villages(user)
            if accessible_villages is None:
                return BusinessGroup.objects.all()
            return BusinessGroup.objects.filter(
                members__household__village__in=accessible_villages
            ).distinct()
        return BusinessGroup.objects.none()

    # Built-in admin roles see all
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return BusinessGroup.objects.all()

    # FA and Mentor see only their assigned villages
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None:
            return BusinessGroup.objects.filter(
                members__household__village__in=assigned_villages
            ).distinct()
        return BusinessGroup.objects.none()

    return BusinessGroup.objects.none()


def get_filtered_savings_groups(user):
    """Get savings groups based on user role and assigned villages.
    Supports both built-in roles and custom roles with geographic restrictions.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets all
    if user.is_superuser:
        return BusinessSavingsGroup.objects.all()

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active and custom_role.has_permission('savings_groups', 'read'):
            accessible_villages = get_user_accessible_villages(user)
            if accessible_villages is None:
                return BusinessSavingsGroup.objects.all()
            return BusinessSavingsGroup.objects.filter(
                bsg_members__household__village__in=accessible_villages
            ).distinct()
        return BusinessSavingsGroup.objects.none()

    # Built-in admin roles see all
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return BusinessSavingsGroup.objects.all()

    # FA and Mentor see only their assigned villages
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None:
            return BusinessSavingsGroup.objects.filter(
                bsg_members__household__village__in=accessible_villages
            ).distinct()
        return BusinessSavingsGroup.objects.none()

    return BusinessSavingsGroup.objects.none()


def get_filtered_grants(user):
    """Get grants based on user role and assigned villages.
    Supports both built-in roles and custom roles with geographic restrictions.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets all
    if user.is_superuser:
        sb_grants = SBGrant.objects.all()
        pr_grants = PRGrant.objects.all()
        return sb_grants, pr_grants

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active and custom_role.has_permission('grants', 'read'):
            accessible_villages = get_user_accessible_villages(user)
            if accessible_villages is None:
                return SBGrant.objects.all(), PRGrant.objects.all()
            sb_grants = SBGrant.objects.filter(household__village__in=accessible_villages)
            pr_grants = PRGrant.objects.filter(household__village__in=accessible_villages)
            return sb_grants, pr_grants
        return SBGrant.objects.none(), PRGrant.objects.none()

    # Built-in admin roles see all
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return SBGrant.objects.all(), PRGrant.objects.all()

    # FA and Mentor see only their assigned villages
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None:
            sb_grants = SBGrant.objects.filter(household__village__in=assigned_villages)
            pr_grants = PRGrant.objects.filter(household__village__in=assigned_villages)
            return sb_grants, pr_grants
        return SBGrant.objects.none(), PRGrant.objects.none()

    return SBGrant.objects.none(), PRGrant.objects.none()


def get_filtered_training_data(user):
    """Get training data based on user role and assigned villages.
    Supports both built-in roles and custom roles with geographic restrictions.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets all
    if user.is_superuser:
        return Training.objects.all(), HouseholdTrainingEnrollment.objects.all()

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active and custom_role.has_permission('training', 'read'):
            accessible_villages = get_user_accessible_villages(user)
            if accessible_villages is None:
                return Training.objects.all(), HouseholdTrainingEnrollment.objects.all()
            enrollments = HouseholdTrainingEnrollment.objects.filter(
                household__village__in=accessible_villages
            )
            training_ids = enrollments.values_list('training_id', flat=True).distinct()
            trainings = Training.objects.filter(id__in=training_ids)
            return trainings, enrollments
        return Training.objects.none(), HouseholdTrainingEnrollment.objects.none()

    # Built-in admin roles see all
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return Training.objects.all(), HouseholdTrainingEnrollment.objects.all()

    # FA and Mentor see only their assigned villages
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None:
            enrollments = HouseholdTrainingEnrollment.objects.filter(
                household__village__in=assigned_villages
            )
            training_ids = enrollments.values_list('training_id', flat=True).distinct()
            trainings = Training.objects.filter(id__in=training_ids)
            return trainings, enrollments
        return Training.objects.none(), HouseholdTrainingEnrollment.objects.none()

    return Training.objects.none(), HouseholdTrainingEnrollment.objects.none()


def get_filtered_mentoring_data(user):
    """Get mentoring data based on user role and assigned villages.
    Supports both built-in roles and custom roles with geographic restrictions.
    """
    user_role = getattr(user, 'role', None)

    # Superuser gets all
    if user.is_superuser:
        return MentoringVisit.objects.all(), PhoneNudge.objects.all()

    # Check custom role first
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active and custom_role.has_permission('training', 'read'):
            accessible_villages = get_user_accessible_villages(user)
            if accessible_villages is None:
                return MentoringVisit.objects.all(), PhoneNudge.objects.all()
            visits = MentoringVisit.objects.filter(household__village__in=accessible_villages)
            nudges = PhoneNudge.objects.filter(household__village__in=accessible_villages)
            return visits, nudges
        return MentoringVisit.objects.none(), PhoneNudge.objects.none()

    # Built-in admin roles see all
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return MentoringVisit.objects.all(), PhoneNudge.objects.all()

    # Mentor sees only their own logs
    if user_role == 'mentor':
        return MentoringVisit.objects.filter(mentor=user), PhoneNudge.objects.filter(mentor=user)

    # FA sees logs for households in their assigned villages
    if user_role == 'field_associate':
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None:
            visits = MentoringVisit.objects.filter(household__village__in=assigned_villages)
            nudges = PhoneNudge.objects.filter(household__village__in=assigned_villages)
            return visits, nudges
        return MentoringVisit.objects.none(), PhoneNudge.objects.none()

    return MentoringVisit.objects.none(), PhoneNudge.objects.none()


def get_user_scope_message(user):
    """Generate a message describing the user's data access scope."""
    user_role = getattr(user, 'role', None)

    if user.is_superuser:
        return "Showing all data (Administrator)"

    # Check custom role
    if user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        custom_role = user.custom_role
        if custom_role.is_active:
            scope = custom_role.geographic_scope
            if scope == 'all':
                return f"Showing all data (Custom Role: {custom_role.name})"
            elif scope == 'county':
                return f"Showing data for {custom_role.allowed_county} County (Custom Role: {custom_role.name})"
            elif scope == 'subcounty':
                subcounties = ', '.join(custom_role.allowed_subcounties[:3])
                if len(custom_role.allowed_subcounties) > 3:
                    subcounties += f" and {len(custom_role.allowed_subcounties) - 3} more"
                return f"Showing data for Sub-Counties: {subcounties} (Custom Role: {custom_role.name})"
            elif scope == 'villages':
                count = custom_role.allowed_villages.count()
                villages = list(custom_role.allowed_villages.values_list('name', flat=True)[:3])
                village_names = ', '.join(villages)
                if count > 3:
                    village_names += f" and {count - 3} more"
                return f"Showing data for villages: {village_names} (Custom Role: {custom_role.name})"
        return "No data access (Custom Role inactive)"

    # Built-in admin roles
    if user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        return "Showing all data"

    # FA and Mentor
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_accessible_villages(user)
        if assigned_villages is not None and assigned_villages.exists():
            village_names = list(assigned_villages.values_list('name', flat=True)[:5])
            if assigned_villages.count() > 5:
                village_names.append(f"... and {assigned_villages.count() - 5} more")
            return f"Showing data for your assigned villages: {', '.join(village_names)}"
        return "No villages assigned to you. Contact your supervisor."

    return "Limited data access based on your role"


@login_required
def report_list(request):
    """Reports dashboard view - filtered by user role and custom role permissions"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check if user has permission to access reports
    if not can_access_reports(user):
        messages.error(request, 'You do not have permission to access reports.')
        return redirect('dashboard:home')

    # Get filtered data based on role (supports custom roles)
    households = get_filtered_households(user)
    business_groups = get_filtered_business_groups(user)
    savings_groups = get_filtered_savings_groups(user)

    # Generate statistics based on filtered data
    reports_data = {
        'total_households': households.count(),
        'active_programs': HouseholdProgram.objects.filter(
            household__in=households,
            participation_status='active'
        ).count(),
        'graduated_programs': HouseholdProgram.objects.filter(
            household__in=households,
            participation_status='graduated'
        ).count(),
        'total_business_groups': business_groups.count(),
        'total_savings_groups': savings_groups.count(),
    }

    # Check if user can see mentoring logs (custom roles check training permission)
    mentor_logs_visible = False
    if user.is_superuser or user_role in ['me_staff', 'ict_admin', 'field_associate', 'mentor', 'program_manager']:
        mentor_logs_visible = True
    elif user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        if user.custom_role.is_active and user.custom_role.has_permission('training', 'read'):
            mentor_logs_visible = True

    if mentor_logs_visible:
        from datetime import timedelta
        thirty_days_ago = timezone.now().date() - timedelta(days=30)

        # Use the new helper function that supports custom roles
        visits_query, nudges_query = get_filtered_mentoring_data(user)

        reports_data['total_house_visits'] = visits_query.count()
        reports_data['total_phone_calls'] = nudges_query.count()
        reports_data['recent_house_visits'] = visits_query.filter(visit_date__gte=thirty_days_ago).count()
        reports_data['recent_phone_calls'] = nudges_query.filter(call_date__gte=thirty_days_ago).count()

    # Get grants data if user has permission
    grants_visible = False
    if user.is_superuser or user_role in ['me_staff', 'ict_admin', 'program_manager', 'county_executive', 'county_assembly', 'field_associate']:
        grants_visible = True
    elif user_role == 'custom' and hasattr(user, 'custom_role') and user.custom_role:
        if user.custom_role.is_active and user.custom_role.has_permission('grants', 'read'):
            grants_visible = True

    if grants_visible:
        sb_grants, pr_grants = get_filtered_grants(user)
        reports_data['total_sb_grants'] = sb_grants.count()
        reports_data['total_pr_grants'] = pr_grants.count()

    # Use the new scope message helper
    scope_message = get_user_scope_message(user)

    context = {
        'reports_data': reports_data,
        'mentor_logs_visible': mentor_logs_visible,
        'grants_visible': grants_visible,
        'page_title': 'Reports & Analytics',
        'user_role': user_role,
        'scope_message': scope_message,
    }

    return render(request, 'reports/report_list.html', context)


@login_required
def download_household_report(request):
    """Download household registration report as CSV - filtered by role"""
    user = request.user

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="household_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Household Name', 'Head of Household', 'Village', 'Parish', 'Subcounty', 'County',
        'Members Count', 'Total Members', 'Program Participants', 'Phone Number', 'Registration Date'
    ])

    # Get filtered households based on role
    households = get_filtered_households(user).select_related('village').prefetch_related('members')

    for household in households:
        program_participants = household.members.filter(is_program_participant=True).count()
        head_of_household = household.members.filter(relationship_to_head='head').first()
        head_name = head_of_household.name if head_of_household else 'Not specified'

        writer.writerow([
            household.name,
            head_name,
            household.village.name if household.village else '',
            '',  # parish not available in current model
            household.village.subcounty if household.village else '',
            household.village.country if household.village else '',
            getattr(household, 'members_count', household.members.count()),
            household.members.count(),
            program_participants,
            household.phone_number or '',
            household.created_at.strftime('%Y-%m-%d') if household.created_at else ''
        ])

    return response


@login_required
def download_ppi_report(request):
    """Download PPI assessment report as CSV - filtered by role"""
    user = request.user

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ppi_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Household Name', 'Village', 'Subcounty', 'PPI Name', 'Eligibility Score',
        'Assessment Date', 'Created At'
    ])

    # Get filtered households
    households = get_filtered_households(user)

    ppi_query = PPI.objects.filter(
        household__in=households
    ).select_related('household', 'household__village', 'household__village__subcounty_obj').order_by('-assessment_date')

    for ppi in ppi_query:
        writer.writerow([
            ppi.household.name,
            ppi.household.village.name if ppi.household.village else '',
            ppi.household.village.subcounty_obj.name if ppi.household.village and ppi.household.village.subcounty_obj else '',
            ppi.name or 'PPI Assessment',
            ppi.eligibility_score,
            ppi.assessment_date.strftime('%Y-%m-%d'),
            ppi.created_at.strftime('%Y-%m-%d %H:%M:%S') if ppi.created_at else ''
        ])

    return response


@login_required
def download_program_participation_report(request):
    """Download program participation report as CSV - filtered by role"""
    user = request.user

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="program_participation_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Household Name', 'Village', 'Program Name', 'Participation Status',
        'Enrollment Date', 'Graduation Date', 'Progress (%)'
    ])

    # Get filtered households
    households = get_filtered_households(user)

    participation_query = HouseholdProgram.objects.filter(
        household__in=households
    ).select_related('household', 'household__village', 'program')

    for participation in participation_query:
        writer.writerow([
            participation.household.name,
            participation.household.village.name if participation.household.village else '',
            participation.program.name,
            participation.get_participation_status_display(),
            participation.enrollment_date.strftime('%Y-%m-%d') if participation.enrollment_date else '',
            participation.graduation_date.strftime('%Y-%m-%d') if participation.graduation_date else '',
            participation.progress_percentage or 0
        ])

    return response


@login_required
def download_business_groups_report(request):
    """Download business groups report as CSV - filtered by role"""
    user = request.user

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="business_groups_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Group Name', 'Business Type', 'Business Detail', 'Formation Date',
        'Group Size', 'Members Count', 'Health Status', 'Participation Status', 'Program'
    ])

    # Get filtered business groups
    groups = get_filtered_business_groups(user).select_related('program').prefetch_related('members')

    for group in groups:
        writer.writerow([
            group.name,
            group.get_business_type_display(),
            group.business_type_detail,
            group.formation_date.strftime('%Y-%m-%d'),
            group.group_size,
            group.members.count(),
            group.get_current_business_health_display(),
            group.get_participation_status_display(),
            group.program.name if group.program else ''
        ])

    return response


@login_required
def download_savings_groups_report(request):
    """Download savings groups report as CSV - filtered by role"""
    user = request.user

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="savings_groups_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Group Name', 'Formation Date', 'Members Count', 'Savings to Date (KES)',
        'Meeting Day', 'Meeting Location', 'Active Status'
    ])

    # Get filtered savings groups
    groups = get_filtered_savings_groups(user).prefetch_related('bsg_members')

    for group in groups:
        writer.writerow([
            group.name,
            group.formation_date.strftime('%Y-%m-%d'),
            group.bsg_members.count(),
            f"{group.savings_to_date:,.2f}",
            group.meeting_day,
            group.meeting_location,
            'Active' if group.is_active else 'Inactive'
        ])

    return response


@login_required
def download_grants_report(request):
    """Download grant disbursement report as CSV - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="grants_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Grant Type', 'Applicant Name', 'Applicant Type', 'Business Type', 'Grant Amount (KES)',
        'Status', 'Disbursement Status', 'Disbursement Date', 'Application Date'
    ])

    # Get filtered households for filtering grants
    households = get_filtered_households(user)
    business_groups = get_filtered_business_groups(user)

    # SB Grants - filter based on role
    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        sb_grants = SBGrant.objects.all()
        pr_grants = PRGrant.objects.all()
    else:
        sb_grants = SBGrant.objects.filter(
            Q(household__in=households) | Q(business_group__in=business_groups)
        )
        pr_grants = PRGrant.objects.filter(
            Q(household__in=households) | Q(business_group__in=business_groups)
        )

    for grant in sb_grants.select_related('business_group', 'household', 'savings_group'):
        business_type = grant.business_group.get_business_type_display() if grant.business_group else 'N/A'

        writer.writerow([
            'SB Grant',
            grant.get_applicant_name(),
            grant.get_applicant_type().replace('_', ' ').title(),
            business_type,
            f"{grant.get_grant_amount():,.2f}",
            grant.get_status_display(),
            grant.get_disbursement_status_display(),
            grant.disbursement_date.strftime('%Y-%m-%d') if grant.disbursement_date else '',
            grant.application_date.strftime('%Y-%m-%d') if grant.application_date else ''
        ])

    for grant in pr_grants.select_related('business_group', 'household', 'savings_group'):
        business_type = grant.business_group.get_business_type_display() if grant.business_group else 'N/A'

        writer.writerow([
            'PR Grant',
            grant.get_applicant_name(),
            grant.get_applicant_type().replace('_', ' ').title(),
            business_type,
            f"{grant.grant_amount:,.2f}",
            grant.get_status_display(),
            'N/A',
            grant.disbursement_date.strftime('%Y-%m-%d') if grant.disbursement_date else '',
            grant.application_date.strftime('%Y-%m-%d') if grant.application_date else ''
        ])

    return response


@login_required
def download_training_report(request):
    """Download training attendance report as CSV - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="training_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Training Name', 'Module ID', 'BM Cycle', 'Status', 'Start Date', 'End Date',
        'Enrolled Households', 'Completed Households', 'Completion Rate (%)'
    ])

    # Get filtered households
    households = get_filtered_households(user)

    # Filter trainings based on role
    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        trainings = Training.objects.all()
    else:
        # FA/Mentor see trainings that have enrollments from their assigned households
        trainings = Training.objects.filter(
            enrolled_households__household__in=households
        ).distinct()

    for training in trainings.select_related('bm_cycle').prefetch_related('enrolled_households'):
        # Count only enrollments from filtered households
        if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
            enrolled_count = training.enrolled_households.count()
            completed_count = training.enrolled_households.filter(enrollment_status='completed').count()
        else:
            enrolled_count = training.enrolled_households.filter(household__in=households).count()
            completed_count = training.enrolled_households.filter(
                household__in=households,
                enrollment_status='completed'
            ).count()

        completion_rate = (completed_count / enrolled_count * 100) if enrolled_count > 0 else 0

        writer.writerow([
            training.name,
            training.module_id,
            training.bm_cycle.bm_cycle_name if training.bm_cycle else 'N/A',
            training.get_status_display(),
            training.start_date.strftime('%Y-%m-%d') if training.start_date else '',
            training.end_date.strftime('%Y-%m-%d') if training.end_date else '',
            enrolled_count,
            completed_count,
            f"{completion_rate:.1f}"
        ])

    return response


@login_required
def download_mentoring_report(request):
    """Download mentoring activities report as CSV - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions
    if not (user.is_superuser or user_role in ['me_staff', 'ict_admin', 'field_associate', 'mentor', 'program_manager']):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="error.csv"'
        writer = csv.writer(response)
        writer.writerow(['Error', 'You do not have permission to access this report'])
        return response

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mentoring_full_log_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Activity Type', 'Household', 'Village', 'Subcounty', 'Mentor', 'Mentor Email',
        'Date', 'Time', 'Topic/Type', 'Duration (minutes)', 'Successful Contact',
        'Notes', 'Created At', 'Record ID'
    ])

    # Filter based on user role
    if user_role == 'mentor' and not user.is_superuser:
        # Mentors only see their own logs
        visits_query = MentoringVisit.objects.filter(mentor=user)
        nudges_query = PhoneNudge.objects.filter(mentor=user)
    elif user_role == 'field_associate':
        # FA sees logs for households in their assigned villages
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            visits_query = MentoringVisit.objects.filter(household__village__in=assigned_villages)
            nudges_query = PhoneNudge.objects.filter(household__village__in=assigned_villages)
        else:
            visits_query = MentoringVisit.objects.none()
            nudges_query = PhoneNudge.objects.none()
    else:
        # Admin roles see all
        visits_query = MentoringVisit.objects.all()
        nudges_query = PhoneNudge.objects.all()

    visits_query = visits_query.select_related('household', 'household__village', 'household__village__subcounty_obj', 'mentor')
    nudges_query = nudges_query.select_related('household', 'household__village', 'household__village__subcounty_obj', 'mentor')

    # Apply date filters if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    mentor_id = request.GET.get('mentor_id')

    if date_from:
        visits_query = visits_query.filter(visit_date__gte=date_from)
        nudges_query = nudges_query.filter(call_date__gte=date_from)

    if date_to:
        visits_query = visits_query.filter(visit_date__lte=date_to)
        nudges_query = nudges_query.filter(call_date__lte=date_to)

    if mentor_id and user_role != 'mentor':
        visits_query = visits_query.filter(mentor_id=mentor_id)
        nudges_query = nudges_query.filter(mentor_id=mentor_id)

    # Mentoring Visits
    for visit in visits_query.order_by('-visit_date'):
        writer.writerow([
            'House Visit',
            visit.household.name,
            visit.household.village.name if visit.household.village else '',
            visit.household.village.subcounty_obj.name if visit.household.village and visit.household.village.subcounty_obj else '',
            visit.mentor.get_full_name() if visit.mentor else '',
            visit.mentor.email if visit.mentor else '',
            visit.visit_date.strftime('%Y-%m-%d') if visit.visit_date else '',
            visit.visit_time.strftime('%H:%M') if hasattr(visit, 'visit_time') and visit.visit_time else '',
            visit.topic or '',
            getattr(visit, 'duration_minutes', ''),
            'Yes',
            visit.notes or '',
            visit.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(visit, 'created_at') and visit.created_at else '',
            f"VISIT-{visit.id}"
        ])

    # Phone Nudges
    for nudge in nudges_query.order_by('-call_date'):
        call_date_str = ''
        call_time_str = ''

        if hasattr(nudge.call_date, 'date'):
            call_date_str = nudge.call_date.strftime('%Y-%m-%d')
            call_time_str = nudge.call_date.strftime('%H:%M')
        else:
            call_date_str = nudge.call_date.strftime('%Y-%m-%d') if nudge.call_date else ''

        writer.writerow([
            'Phone Call',
            nudge.household.name,
            nudge.household.village.name if nudge.household.village else '',
            nudge.household.village.subcounty_obj.name if nudge.household.village and nudge.household.village.subcounty_obj else '',
            nudge.mentor.get_full_name() if nudge.mentor else '',
            nudge.mentor.email if nudge.mentor else '',
            call_date_str,
            call_time_str,
            nudge.get_nudge_type_display() if hasattr(nudge, 'get_nudge_type_display') else nudge.nudge_type,
            nudge.duration_minutes if nudge.duration_minutes else '',
            'Yes' if nudge.successful_contact else 'No',
            nudge.notes or '',
            nudge.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(nudge, 'created_at') and nudge.created_at else '',
            f"CALL-{nudge.id}"
        ])

    return response


@login_required
def download_geographic_report(request):
    """Download geographic analysis report as CSV - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="geographic_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'County', 'Subcounty', 'Parish', 'Village', 'Total Households',
        'Active Programs', 'Business Groups', 'Savings Groups', 'Mentors Assigned'
    ])

    from core.models import Village

    # Filter villages based on role
    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        villages = Village.objects.all()
    else:
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            villages = assigned_villages
        else:
            villages = Village.objects.none()

    for village in villages:
        households = Household.objects.filter(village=village)
        active_programs = HouseholdProgram.objects.filter(
            household__village=village,
            participation_status='active'
        ).count()

        business_groups = BusinessGroup.objects.filter(
            members__household__village=village
        ).distinct().count()

        savings_groups = 0

        writer.writerow([
            village.country,
            village.subcounty,
            '',
            village.name,
            households.count(),
            active_programs,
            business_groups,
            savings_groups,
            0
        ])

    return response


@login_required
def performance_dashboard(request):
    """Performance dashboard with key metrics and charts - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Get filtered data
    households = get_filtered_households(user)
    business_groups = get_filtered_business_groups(user)
    savings_groups = get_filtered_savings_groups(user)

    # Calculate key performance indicators
    total_households = households.count()
    active_programs = HouseholdProgram.objects.filter(
        household__in=households,
        participation_status='active'
    ).count()
    graduated_programs = HouseholdProgram.objects.filter(
        household__in=households,
        participation_status='graduated'
    ).count()
    total_business_groups = business_groups.count()
    total_savings_groups = savings_groups.count()

    # Program participation statistics
    program_stats = []
    from core.models import Program
    for program in Program.objects.all():
        enrolled = HouseholdProgram.objects.filter(
            program=program,
            household__in=households
        ).count()
        active = HouseholdProgram.objects.filter(
            program=program,
            household__in=households,
            participation_status='active'
        ).count()
        graduated = HouseholdProgram.objects.filter(
            program=program,
            household__in=households,
            participation_status='graduated'
        ).count()
        if enrolled > 0:  # Only show programs with data
            program_stats.append({
                'name': program.name,
                'enrolled': enrolled,
                'active': active,
                'graduated': graduated,
                'completion_rate': (graduated / enrolled * 100) if enrolled > 0 else 0
            })

    # Geographic distribution - filtered by role
    from core.models import Village
    geographic_stats = []

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        villages = Village.objects.all()[:10]
    else:
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            villages = assigned_villages[:10]
        else:
            villages = Village.objects.none()

    for village in villages:
        household_count = Household.objects.filter(village=village).count()
        active_count = HouseholdProgram.objects.filter(
            household__village=village,
            participation_status='active'
        ).count()
        geographic_stats.append({
            'village': village.name,
            'subcounty': village.subcounty,
            'households': household_count,
            'active_programs': active_count
        })

    # Show user's scope
    scope_message = None
    if user_role in ['field_associate', 'mentor']:
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            village_names = list(assigned_villages.values_list('name', flat=True)[:5])
            if assigned_villages.count() > 5:
                village_names.append(f"... and {assigned_villages.count() - 5} more")
            scope_message = f"Showing data for your assigned villages: {', '.join(village_names)}"

    context = {
        'page_title': 'Program Performance Dashboard',
        'total_households': total_households,
        'active_programs': active_programs,
        'graduated_programs': graduated_programs,
        'total_business_groups': total_business_groups,
        'total_savings_groups': total_savings_groups,
        'program_stats': program_stats,
        'geographic_stats': geographic_stats,
        'graduation_rate': (graduated_programs / total_households * 100) if total_households > 0 else 0,
        'user_role': user_role,
        'scope_message': scope_message,
    }

    return render(request, 'reports/performance_dashboard.html', context)


@login_required
def custom_report_builder(request):
    """Custom report builder interface - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from core.models import Village, Program

    # Filter villages based on role
    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        villages = Village.objects.all()
    else:
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            villages = assigned_villages
        else:
            villages = Village.objects.none()

    programs = Program.objects.all()

    # Available report types
    report_types = [
        ('households', 'Household Report'),
        ('business_groups', 'Business Groups Report'),
        ('savings_groups', 'Savings Groups Report'),
        ('training', 'Training Report'),
        ('ppi', 'PPI Assessment Report'),
        ('geographic', 'Geographic Analysis'),
    ]

    context = {
        'page_title': 'Custom Report Builder',
        'villages': villages,
        'programs': programs,
        'report_types': report_types,
        'user_role': user_role,
    }

    return render(request, 'reports/custom_report_builder.html', context)


@login_required
def download_custom_report(request):
    """Download custom report based on user selections - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    report_type = request.GET.get('report_type', 'households')
    village_id = request.GET.get('village')
    program_id = request.GET.get('program')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    output_format = request.GET.get('output_format', 'csv')

    # Handle PDF format
    if output_format == 'pdf':
        return _generate_custom_pdf_report(request, report_type, village_id, program_id, date_from, date_to)

    # CSV format (default)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="custom_{report_type}_report_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)

    if report_type == 'households':
        writer.writerow(['Household Name', 'Village', 'SubCounty', 'Phone Number', 'Members', 'Registration Date'])

        households = get_filtered_households(user)

        if village_id:
            households = households.filter(village_id=village_id)
        if date_from:
            households = households.filter(created_at__gte=date_from)
        if date_to:
            households = households.filter(created_at__lte=date_to)

        for household in households.select_related('village', 'village__subcounty_obj'):
            writer.writerow([
                household.name,
                household.village.name if household.village else '',
                household.village.subcounty_obj.name if household.village and household.village.subcounty_obj else '',
                household.phone_number or '',
                household.members.count(),
                household.created_at.strftime('%Y-%m-%d') if household.created_at else ''
            ])

    elif report_type == 'business_groups':
        writer.writerow(['Group Name', 'Village', 'Business Type', 'Formation Date', 'Members', 'Status'])

        groups = get_filtered_business_groups(user)

        if village_id:
            groups = groups.filter(members__household__village_id=village_id).distinct()

        for group in groups:
            village_name = ''
            if group.members.exists():
                first_member = group.members.first()
                if first_member.household.village:
                    village_name = first_member.household.village.name

            writer.writerow([
                group.name,
                village_name,
                group.get_business_type_display(),
                group.formation_date.strftime('%Y-%m-%d'),
                group.members.count(),
                group.status if hasattr(group, 'status') else 'Active'
            ])

    elif report_type == 'savings_groups':
        writer.writerow(['Group Name', 'Members', 'Savings (KES)', 'Meeting Day', 'Active', 'Formation Date'])

        groups = get_filtered_savings_groups(user)

        if village_id:
            groups = groups.filter(bsg_members__household__village_id=village_id).distinct()

        for g in groups.prefetch_related('bsg_members'):
            writer.writerow([
                g.name,
                g.bsg_members.count(),
                f"{g.savings_to_date:,.2f}",
                g.meeting_day or '-',
                'Yes' if g.is_active else 'No',
                g.formation_date.strftime('%Y-%m-%d') if g.formation_date else ''
            ])

    elif report_type == 'training':
        writer.writerow(['Training Name', 'Module', 'Status', 'Start Date', 'Enrolled', 'Completed'])

        households = get_filtered_households(user)

        if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
            trainings = Training.objects.all()
        else:
            trainings = Training.objects.filter(
                enrolled_households__household__in=households
            ).distinct()

        if date_from:
            trainings = trainings.filter(start_date__gte=date_from)
        if date_to:
            trainings = trainings.filter(start_date__lte=date_to)

        for t in trainings.select_related('bm_cycle').prefetch_related('enrolled_households'):
            enrolled = t.enrolled_households.count()
            completed_count = t.enrolled_households.filter(enrollment_status='completed').count()
            writer.writerow([
                t.name,
                t.module_id or '-',
                t.status or '-',
                t.start_date.strftime('%Y-%m-%d') if t.start_date else '',
                enrolled,
                completed_count
            ])

    elif report_type == 'ppi':
        from households.models import PPI
        writer.writerow(['Household', 'Village', 'Assessment Name', 'Eligibility Score', 'Assessment Date'])

        households = get_filtered_households(user)

        if village_id:
            households = households.filter(village_id=village_id)

        assessments = PPI.objects.filter(household__in=households).select_related('household', 'household__village')

        if date_from:
            assessments = assessments.filter(assessment_date__gte=date_from)
        if date_to:
            assessments = assessments.filter(assessment_date__lte=date_to)

        for a in assessments:
            writer.writerow([
                a.household.name,
                a.household.village.name if a.household.village else '',
                a.name or '',
                a.eligibility_score,
                a.assessment_date.strftime('%Y-%m-%d') if a.assessment_date else ''
            ])

    elif report_type == 'geographic':
        from core.models import Village
        from django.db.models import Count

        writer.writerow(['Village', 'SubCounty', 'Households', 'Business Groups', 'Savings Groups'])

        if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
            villages = Village.objects.all()
        else:
            assigned_villages = get_user_assigned_villages(user)
            if assigned_villages:
                villages = assigned_villages
            else:
                villages = Village.objects.none()

        village_stats = villages.annotate(
            household_count=Count('household', distinct=True)
        ).select_related('subcounty_obj')

        for v in village_stats:
            # Count business groups and savings groups for this village
            bg_count = BusinessGroup.objects.filter(
                members__household__village=v
            ).distinct().count()
            sg_count = BusinessSavingsGroup.objects.filter(
                bsg_members__household__village=v
            ).distinct().count()

            writer.writerow([
                v.name,
                v.subcounty_obj.name if v.subcounty_obj else v.subcounty or '',
                v.household_count,
                bg_count,
                sg_count
            ])

    else:
        writer.writerow(['Report Type', 'Status'])
        writer.writerow([report_type, 'Not implemented yet'])

    return response


def _generate_custom_pdf_report(request, report_type, village_id, program_id, date_from, date_to):
    """Generate custom PDF report based on report type and filters"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from io import BytesIO
    from django.db.models import Count, Sum

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
    except ImportError:
        # Fall back to CSV if reportlab not available
        return download_custom_report(request)

    styles = _get_pdf_styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    report_titles = {
        'households': 'Custom Household Report',
        'business_groups': 'Custom Business Groups Report',
        'savings_groups': 'Custom Savings Groups Report',
        'training': 'Custom Training Report',
        'ppi': 'Custom PPI Assessment Report',
        'geographic': 'Custom Geographic Analysis Report'
    }

    # Title
    elements.append(Paragraph(report_titles.get(report_type, 'Custom Report'), styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Paragraph(f"Generated by: {user.get_full_name() or user.username}", styles['normal']))

    # Add filter info
    filter_info = []
    if village_id:
        from core.models import Village
        try:
            village = Village.objects.get(id=village_id)
            filter_info.append(f"Village: {village.name}")
        except Village.DoesNotExist:
            pass
    if date_from:
        filter_info.append(f"From: {date_from}")
    if date_to:
        filter_info.append(f"To: {date_to}")

    if filter_info:
        elements.append(Paragraph(f"Filters: {', '.join(filter_info)}", styles['normal']))

    elements.append(Spacer(1, 20))

    if report_type == 'households':
        elements = _build_households_pdf(elements, user, village_id, date_from, date_to, styles)

    elif report_type == 'business_groups':
        elements = _build_business_groups_pdf(elements, user, village_id, styles)

    elif report_type == 'savings_groups':
        elements = _build_savings_groups_pdf(elements, user, village_id, styles)

    elif report_type == 'training':
        elements = _build_training_pdf(elements, user, user_role, date_from, date_to, styles)

    elif report_type == 'ppi':
        elements = _build_ppi_pdf(elements, user, village_id, date_from, date_to, styles)

    elif report_type == 'geographic':
        elements = _build_geographic_pdf(elements, user, user_role, styles)

    else:
        elements.append(Paragraph(f"Report type '{report_type}' not yet implemented for PDF.", styles['normal']))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="custom_{report_type}_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


def _build_households_pdf(elements, user, village_id, date_from, date_to, styles):
    """Build household PDF content"""
    from django.db.models import Count
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer

    households = get_filtered_households(user)

    if village_id:
        households = households.filter(village_id=village_id)
    if date_from:
        households = households.filter(created_at__gte=date_from)
    if date_to:
        households = households.filter(created_at__lte=date_to)

    # Summary
    total = households.count()
    with_phone = households.exclude(phone_number__isnull=True).exclude(phone_number='').count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Households', str(total)],
        ['With Phone Number', str(with_phone)],
        ['Phone Coverage', f"{(with_phone/total*100):.1f}%" if total > 0 else '0%'],
    ]
    elements.append(_create_summary_table(summary_data, '#3498db'))
    elements.append(Spacer(1, 20))

    # Village distribution pie chart
    village_dist = households.values('village__name').annotate(count=Count('id')).order_by('-count')[:10]

    if village_dist and total > 0:
        elements.append(Paragraph("Distribution by Village (Top 10)", styles['heading']))

        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 0
        pie.width = 150
        pie.height = 150
        pie.data = [v['count'] for v in village_dist]
        pie.labels = [v['village__name'][:15] if v['village__name'] else 'Unknown' for v in village_dist]
        pie.slices.strokeWidth = 0.5
        colors_list = [colors.HexColor(c) for c in ['#3498db', '#27ae60', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22', '#2ecc71', '#95a5a6']]
        for i, color in enumerate(colors_list[:len(village_dist)]):
            pie.slices[i].fillColor = color
        drawing.add(pie)
        elements.append(drawing)
        elements.append(Spacer(1, 10))

        # Table
        village_data = [['Village', 'Households', 'Percentage']]
        for v in village_dist:
            pct = (v['count'] / total * 100) if total > 0 else 0
            village_data.append([
                v['village__name'] or 'Unknown',
                str(v['count']),
                f"{pct:.1f}%"
            ])
        elements.append(_create_data_table(village_data, [3*inch, 1.5*inch, 1.5*inch], '#27ae60'))

    elements.append(Spacer(1, 20))

    # Household details table
    elements.append(Paragraph("Household Details (First 50)", styles['heading']))
    hh_data = [['Name', 'Village', 'Phone', 'Members']]
    for hh in households.select_related('village').prefetch_related('members')[:50]:
        hh_data.append([
            hh.name[:30],
            hh.village.name[:20] if hh.village else '-',
            hh.phone_number or '-',
            str(hh.members.count())
        ])
    elements.append(_create_data_table(hh_data, [2.5*inch, 2*inch, 1.5*inch, 1*inch]))

    return elements


def _build_business_groups_pdf(elements, user, village_id, styles):
    """Build business groups PDF content"""
    from django.db.models import Count
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer

    groups = get_filtered_business_groups(user)

    if village_id:
        groups = groups.filter(members__household__village_id=village_id).distinct()

    total = groups.count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Business Groups', str(total)],
        ['Total Members', str(sum(g.members.count() for g in groups))],
    ]
    elements.append(_create_summary_table(summary_data, '#27ae60'))
    elements.append(Spacer(1, 20))

    # Business type distribution
    type_dist = groups.values('business_type').annotate(count=Count('id')).order_by('-count')

    if type_dist:
        elements.append(Paragraph("Distribution by Business Type", styles['heading']))
        type_data = [['Business Type', 'Count', 'Percentage']]
        for t in type_dist:
            pct = (t['count'] / total * 100) if total > 0 else 0
            type_data.append([
                t['business_type'] or 'Unknown',
                str(t['count']),
                f"{pct:.1f}%"
            ])
        elements.append(_create_data_table(type_data, [3*inch, 1.5*inch, 1.5*inch], '#27ae60'))
        elements.append(Spacer(1, 20))

    # Group details
    elements.append(Paragraph("Business Group Details (First 50)", styles['heading']))
    bg_data = [['Group Name', 'Business Type', 'Formation Date', 'Members']]
    for g in groups.prefetch_related('members')[:50]:
        bg_data.append([
            g.name[:25],
            g.get_business_type_display()[:20],
            g.formation_date.strftime('%Y-%m-%d'),
            str(g.members.count())
        ])
    elements.append(_create_data_table(bg_data, [2.5*inch, 2*inch, 1.5*inch, 1*inch]))

    return elements


def _build_savings_groups_pdf(elements, user, village_id, styles):
    """Build savings groups PDF content"""
    from django.db.models import Sum, Count
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer

    groups = get_filtered_savings_groups(user)

    if village_id:
        groups = groups.filter(bsg_members__household__village_id=village_id).distinct()

    total = groups.count()
    active = groups.filter(is_active=True).count()
    total_savings = groups.aggregate(total=Sum('savings_to_date'))['total'] or 0

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Savings Groups', str(total)],
        ['Active Groups', str(active)],
        ['Total Savings (KES)', f"{total_savings:,.2f}"],
        ['Avg Savings per Group', f"KES {(total_savings/total):,.2f}" if total > 0 else 'KES 0'],
    ]
    elements.append(_create_summary_table(summary_data, '#9b59b6'))
    elements.append(Spacer(1, 20))

    # Group details
    elements.append(Paragraph("Savings Group Details (First 50)", styles['heading']))
    sg_data = [['Group Name', 'Members', 'Savings (KES)', 'Meeting Day', 'Active']]
    for g in groups.prefetch_related('bsg_members')[:50]:
        sg_data.append([
            g.name[:25],
            str(g.bsg_members.count()),
            f"{g.savings_to_date:,.0f}",
            g.meeting_day or '-',
            'Yes' if g.is_active else 'No'
        ])
    elements.append(_create_data_table(sg_data, [2*inch, 1*inch, 1.5*inch, 1.2*inch, 0.8*inch]))

    return elements


def _build_training_pdf(elements, user, user_role, date_from, date_to, styles):
    """Build training PDF content"""
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer

    households = get_filtered_households(user)

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        trainings = Training.objects.all()
    else:
        trainings = Training.objects.filter(
            enrolled_households__household__in=households
        ).distinct()

    if date_from:
        trainings = trainings.filter(start_date__gte=date_from)
    if date_to:
        trainings = trainings.filter(start_date__lte=date_to)

    total = trainings.count()
    completed = trainings.filter(status='completed').count()
    active = trainings.filter(status='active').count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Trainings', str(total)],
        ['Active', str(active)],
        ['Completed', str(completed)],
        ['Planned', str(trainings.filter(status='planned').count())],
    ]
    elements.append(_create_summary_table(summary_data, '#e67e22'))
    elements.append(Spacer(1, 20))

    # Training details
    elements.append(Paragraph("Training Details (First 30)", styles['heading']))
    tr_data = [['Training Name', 'Module', 'Status', 'Enrolled', 'Completed']]

    for t in trainings.select_related('bm_cycle').prefetch_related('enrolled_households')[:30]:
        enrolled = t.enrolled_households.count()
        completed_count = t.enrolled_households.filter(enrollment_status='completed').count()
        tr_data.append([
            t.name[:25],
            t.module_id or '-',
            t.status or '-',
            str(enrolled),
            str(completed_count)
        ])

    elements.append(_create_data_table(tr_data, [2.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch]))

    return elements


def _build_ppi_pdf(elements, user, village_id, date_from, date_to, styles):
    """Build PPI assessment PDF content"""
    from households.models import PPI
    from django.db.models import Avg
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer

    households = get_filtered_households(user)

    if village_id:
        households = households.filter(village_id=village_id)

    assessments = PPI.objects.filter(household__in=households).select_related('household', 'household__village')

    if date_from:
        assessments = assessments.filter(assessment_date__gte=date_from)
    if date_to:
        assessments = assessments.filter(assessment_date__lte=date_to)

    total = assessments.count()
    avg_score = assessments.aggregate(avg=Avg('eligibility_score'))['avg'] or 0

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Assessments', str(total)],
        ['Average Eligibility Score', f"{avg_score:.1f}"],
        ['Households Assessed', str(assessments.values('household').distinct().count())],
    ]
    elements.append(_create_summary_table(summary_data, '#e74c3c'))
    elements.append(Spacer(1, 20))

    # Assessment details
    elements.append(Paragraph("PPI Assessment Details (First 50)", styles['heading']))
    ppi_data = [['Household', 'Village', 'Assessment', 'Score', 'Date']]

    for a in assessments[:50]:
        ppi_data.append([
            a.household.name[:20],
            a.household.village.name[:15] if a.household.village else '-',
            a.name[:15] if a.name else '-',
            str(a.eligibility_score),
            a.assessment_date.strftime('%Y-%m-%d') if a.assessment_date else '-'
        ])

    elements.append(_create_data_table(ppi_data, [2*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch]))

    return elements


def _build_geographic_pdf(elements, user, user_role, styles):
    """Build geographic analysis PDF content"""
    from core.models import Village
    from django.db.models import Count
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        villages = Village.objects.all()
    else:
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            villages = assigned_villages
        else:
            villages = Village.objects.none()

    village_stats = villages.annotate(
        household_count=Count('household', distinct=True)
    ).select_related('subcounty_obj').order_by('-household_count')

    total_villages = villages.count()
    total_households = sum(v.household_count for v in village_stats)

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Villages', str(total_villages)],
        ['Total Households', str(total_households)],
        ['Avg Households per Village', f"{(total_households/total_villages):.1f}" if total_villages > 0 else '0'],
    ]
    elements.append(_create_summary_table(summary_data, '#1abc9c'))
    elements.append(Spacer(1, 20))

    # Village details
    elements.append(Paragraph("Village Details", styles['heading']))
    geo_data = [['Village', 'SubCounty', 'Households', 'Business Groups', 'Savings Groups']]

    for v in village_stats[:50]:
        bg_count = BusinessGroup.objects.filter(
            members__household__village=v
        ).distinct().count()
        sg_count = BusinessSavingsGroup.objects.filter(
            bsg_members__household__village=v
        ).distinct().count()

        geo_data.append([
            v.name[:20],
            v.subcounty_obj.name[:15] if v.subcounty_obj else v.subcounty[:15] if v.subcounty else '-',
            str(v.household_count),
            str(bg_count),
            str(sg_count)
        ])

    elements.append(_create_data_table(geo_data, [2*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch]))

    return elements


@login_required
def mentoring_activities_dashboard(request):
    """
    Comprehensive mentoring activities dashboard with visualizations
    Shows all activities for mentors and FAs based on their role
    """
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions
    if not (user.is_superuser or user_role in ['me_staff', 'ict_admin', 'field_associate', 'mentor', 'program_manager']):
        from django.contrib import messages
        messages.error(request, 'You do not have permission to access mentoring reports.')
        from django.shortcuts import redirect
        return redirect('dashboard:dashboard')

    from datetime import timedelta
    from django.db.models import Count, Sum, Avg
    from django.db.models.functions import TruncMonth, TruncWeek

    # Get mentoring data based on role
    if user_role == 'mentor' and not user.is_superuser:
        # Mentors see their own activities
        visits_query = MentoringVisit.objects.filter(mentor=user)
        nudges_query = PhoneNudge.objects.filter(mentor=user)
        trainings_conducted = Training.objects.filter(assigned_mentor=user)
        scope_title = f"My Mentoring Activities"
    elif user_role == 'field_associate':
        # FA sees activities for all mentors in their assigned villages
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            visits_query = MentoringVisit.objects.filter(household__village__in=assigned_villages)
            nudges_query = PhoneNudge.objects.filter(household__village__in=assigned_villages)
            trainings_conducted = Training.objects.filter(
                attendances__household__village__in=assigned_villages
            ).distinct()
        else:
            visits_query = MentoringVisit.objects.none()
            nudges_query = PhoneNudge.objects.none()
            trainings_conducted = Training.objects.none()
        scope_title = f"Mentoring Activities in My Villages"
    else:
        # Admin roles see all
        visits_query = MentoringVisit.objects.all()
        nudges_query = PhoneNudge.objects.all()
        trainings_conducted = Training.objects.all()
        scope_title = "All Mentoring Activities"

    # Date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    selected_mentor = request.GET.get('mentor_id')

    if date_from:
        visits_query = visits_query.filter(visit_date__gte=date_from)
        nudges_query = nudges_query.filter(call_date__gte=date_from)

    if date_to:
        visits_query = visits_query.filter(visit_date__lte=date_to)
        nudges_query = nudges_query.filter(call_date__lte=date_to)

    if selected_mentor and user_role != 'mentor':
        visits_query = visits_query.filter(mentor_id=selected_mentor)
        nudges_query = nudges_query.filter(mentor_id=selected_mentor)

    # Calculate statistics
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    seven_days_ago = timezone.now().date() - timedelta(days=7)

    stats = {
        'total_visits': visits_query.count(),
        'total_calls': nudges_query.count(),
        'visits_last_30_days': visits_query.filter(visit_date__gte=thirty_days_ago).count(),
        'calls_last_30_days': nudges_query.filter(call_date__gte=thirty_days_ago).count(),
        'visits_last_7_days': visits_query.filter(visit_date__gte=seven_days_ago).count(),
        'calls_last_7_days': nudges_query.filter(call_date__gte=seven_days_ago).count(),
        'unique_households_visited': visits_query.values('household').distinct().count(),
        'unique_households_called': nudges_query.values('household').distinct().count(),
        'avg_visit_duration': visits_query.filter(duration_minutes__isnull=False).aggregate(avg=Avg('duration_minutes'))['avg'] or 0,
        'avg_call_duration': nudges_query.filter(duration_minutes__isnull=False).aggregate(avg=Avg('duration_minutes'))['avg'] or 0,
        'trainings_conducted': trainings_conducted.filter(status='completed').count(),
        'successful_calls': nudges_query.filter(successful_contact=True).count(),
    }

    # Monthly trends for charts (last 6 months)
    six_months_ago = timezone.now().date() - timedelta(days=180)

    monthly_visits = list(visits_query.filter(
        visit_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('visit_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month'))

    monthly_calls = list(nudges_query.filter(
        call_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('call_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month'))

    # Visit types breakdown
    visit_types = list(visits_query.values('visit_type').annotate(count=Count('id')).order_by('-count'))

    # Nudge types breakdown
    nudge_types = list(nudges_query.values('nudge_type').annotate(count=Count('id')).order_by('-count'))

    # Top mentors (for admin views)
    top_mentors = []
    if user_role not in ['mentor']:
        top_mentors = list(visits_query.values(
            'mentor__first_name', 'mentor__last_name', 'mentor__id'
        ).annotate(
            visit_count=Count('id')
        ).order_by('-visit_count')[:10])

    # Recent activities
    recent_visits = visits_query.select_related('household', 'mentor').order_by('-visit_date')[:10]
    recent_calls = nudges_query.select_related('household', 'mentor').order_by('-call_date')[:10]

    # Mentors list for filter (FA and admin only)
    mentors_list = []
    if user_role != 'mentor':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if user_role == 'field_associate' and assigned_villages:
            # Get mentors who have done activities in FA's villages
            mentor_ids = visits_query.values_list('mentor_id', flat=True).distinct()
            mentors_list = User.objects.filter(id__in=mentor_ids).order_by('first_name')
        else:
            mentors_list = User.objects.filter(role='mentor', is_active=True).order_by('first_name')

    # Prepare chart data (JSON serializable)
    import json

    chart_data = {
        'monthly_visits': [
            {'month': m['month'].strftime('%b %Y') if m['month'] else '', 'count': m['count']}
            for m in monthly_visits
        ],
        'monthly_calls': [
            {'month': m['month'].strftime('%b %Y') if m['month'] else '', 'count': m['count']}
            for m in monthly_calls
        ],
        'visit_types': [
            {'type': dict(MentoringVisit.VISIT_TYPE_CHOICES).get(v['visit_type'], v['visit_type']), 'count': v['count']}
            for v in visit_types
        ],
        'nudge_types': [
            {'type': dict(PhoneNudge.NUDGE_TYPE_CHOICES).get(n['nudge_type'], n['nudge_type']), 'count': n['count']}
            for n in nudge_types
        ],
    }

    context = {
        'page_title': scope_title,
        'stats': stats,
        'chart_data': json.dumps(chart_data),
        'top_mentors': top_mentors,
        'recent_visits': recent_visits,
        'recent_calls': recent_calls,
        'mentors_list': mentors_list,
        'user_role': user_role,
        'date_from': date_from,
        'date_to': date_to,
        'selected_mentor': selected_mentor,
    }

    return render(request, 'reports/mentoring_activities_dashboard.html', context)


@login_required
def download_mentoring_pdf_report(request):
    """
    Generate PDF report for mentoring activities with visualizations
    """
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions
    if not (user.is_superuser or user_role in ['me_staff', 'ict_admin', 'field_associate', 'mentor', 'program_manager']):
        from django.contrib import messages
        messages.error(request, 'You do not have permission to download this report.')
        from django.shortcuts import redirect
        return redirect('reports:report_list')

    from io import BytesIO
    from datetime import timedelta
    from django.db.models import Count, Avg

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.piecharts import Pie
    except ImportError:
        # If reportlab is not installed, return CSV instead
        return download_mentoring_report(request)

    # Get data based on role
    if user_role == 'mentor' and not user.is_superuser:
        visits_query = MentoringVisit.objects.filter(mentor=user)
        nudges_query = PhoneNudge.objects.filter(mentor=user)
        report_title = f"My Mentoring Activities Report"
    elif user_role == 'field_associate':
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            visits_query = MentoringVisit.objects.filter(household__village__in=assigned_villages)
            nudges_query = PhoneNudge.objects.filter(household__village__in=assigned_villages)
        else:
            visits_query = MentoringVisit.objects.none()
            nudges_query = PhoneNudge.objects.none()
        report_title = f"Mentoring Activities Report - My Villages"
    else:
        visits_query = MentoringVisit.objects.all()
        nudges_query = PhoneNudge.objects.all()
        report_title = "Mentoring Activities Report - All"

    # Apply date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        visits_query = visits_query.filter(visit_date__gte=date_from)
        nudges_query = nudges_query.filter(call_date__gte=date_from)

    if date_to:
        visits_query = visits_query.filter(visit_date__lte=date_to)
        nudges_query = nudges_query.filter(call_date__lte=date_to)

    # Calculate statistics
    thirty_days_ago = timezone.now().date() - timedelta(days=30)

    total_visits = visits_query.count()
    total_calls = nudges_query.count()
    visits_last_30 = visits_query.filter(visit_date__gte=thirty_days_ago).count()
    calls_last_30 = nudges_query.filter(call_date__gte=thirty_days_ago).count()
    unique_households = visits_query.values('household').distinct().count()
    avg_visit_duration = visits_query.filter(duration_minutes__isnull=False).aggregate(avg=Avg('duration_minutes'))['avg'] or 0

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50')
    )

    elements = []

    # Title
    elements.append(Paragraph(report_title, title_style))
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
    if date_from or date_to:
        date_range = f"Period: {date_from or 'Start'} to {date_to or 'Present'}"
        elements.append(Paragraph(date_range, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Summary Statistics Table
    elements.append(Paragraph("Summary Statistics", heading_style))

    summary_data = [
        ['Metric', 'Value'],
        ['Total House Visits', str(total_visits)],
        ['Total Phone Calls', str(total_calls)],
        ['Visits (Last 30 Days)', str(visits_last_30)],
        ['Calls (Last 30 Days)', str(calls_last_30)],
        ['Unique Households Visited', str(unique_households)],
        ['Avg Visit Duration (mins)', f"{avg_visit_duration:.1f}"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Visit Types Breakdown
    visit_types = visits_query.values('visit_type').annotate(count=Count('id')).order_by('-count')
    if visit_types:
        elements.append(Paragraph("Visit Types Breakdown", heading_style))

        visit_type_data = [['Visit Type', 'Count', 'Percentage']]
        for vt in visit_types:
            pct = (vt['count'] / total_visits * 100) if total_visits > 0 else 0
            visit_type_data.append([
                dict(MentoringVisit.VISIT_TYPE_CHOICES).get(vt['visit_type'], vt['visit_type']),
                str(vt['count']),
                f"{pct:.1f}%"
            ])

        vt_table = Table(visit_type_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        vt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(vt_table)
        elements.append(Spacer(1, 20))

    # Top Mentors (for admin views)
    if user_role not in ['mentor']:
        top_mentors = visits_query.values(
            'mentor__first_name', 'mentor__last_name'
        ).annotate(
            visit_count=Count('id')
        ).order_by('-visit_count')[:10]

        if top_mentors:
            elements.append(Paragraph("Top 10 Mentors by Visits", heading_style))

            mentor_data = [['Mentor Name', 'Visits']]
            for m in top_mentors:
                mentor_data.append([
                    f"{m['mentor__first_name']} {m['mentor__last_name']}",
                    str(m['visit_count'])
                ])

            mentor_table = Table(mentor_data, colWidths=[3*inch, 1.5*inch])
            mentor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(mentor_table)
            elements.append(Spacer(1, 20))

    # Recent Activities
    elements.append(Paragraph("Recent House Visits (Last 10)", heading_style))

    recent_visits = visits_query.select_related('household', 'mentor').order_by('-visit_date')[:10]
    if recent_visits:
        recent_data = [['Date', 'Household', 'Mentor', 'Topic']]
        for v in recent_visits:
            recent_data.append([
                v.visit_date.strftime('%Y-%m-%d') if v.visit_date else '',
                v.household.name[:30] if v.household else '',
                v.mentor.get_full_name()[:20] if v.mentor else '',
                (v.topic[:30] + '...' if len(v.topic) > 30 else v.topic) if v.topic else ''
            ])

        recent_table = Table(recent_data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 2*inch])
        recent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(recent_table)
    else:
        elements.append(Paragraph("No recent visits found.", styles['Normal']))

    # Build PDF
    doc.build(elements)

    # Return response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="mentoring_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'

    return response


@login_required
def download_comprehensive_pdf_report(request):
    """
    Generate comprehensive PDF report with all key metrics and visualizations
    Available to all authenticated users based on their role
    """
    user = request.user
    user_role = getattr(user, 'role', None)

    from io import BytesIO
    from datetime import timedelta
    from django.db.models import Count, Sum, Avg

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    except ImportError:
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="error.txt"'
        response.write('PDF generation requires reportlab library. Please install it with: pip install reportlab')
        return response

    # Get filtered data based on role
    households = get_filtered_households(user)
    business_groups = get_filtered_business_groups(user)
    savings_groups = get_filtered_savings_groups(user)

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, spaceAfter=30, alignment=1)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#2c3e50'))
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, spaceAfter=8)

    elements = []

    # Title Page
    elements.append(Paragraph("UPG Management System", title_style))
    elements.append(Paragraph("Comprehensive Performance Report", styles['Heading2']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Generated by: {user.get_full_name()} ({user_role})", styles['Normal']))

    # Scope information - supports custom roles
    scope_message = get_user_scope_message(user)
    elements.append(Paragraph(f"Data Scope: {scope_message}", styles['Normal']))

    elements.append(Spacer(1, 30))

    # 1. Household Statistics
    elements.append(Paragraph("1. Household Statistics", heading_style))

    total_households = households.count()
    active_programs = HouseholdProgram.objects.filter(household__in=households, participation_status='active').count()
    graduated = HouseholdProgram.objects.filter(household__in=households, participation_status='graduated').count()

    hh_data = [
        ['Metric', 'Value'],
        ['Total Households', str(total_households)],
        ['Active in Programs', str(active_programs)],
        ['Graduated', str(graduated)],
        ['Graduation Rate', f"{(graduated/total_households*100):.1f}%" if total_households > 0 else '0%'],
    ]

    hh_table = Table(hh_data, colWidths=[3*inch, 2*inch])
    hh_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
    ]))
    elements.append(hh_table)
    elements.append(Spacer(1, 20))

    # 2. Business Groups
    elements.append(Paragraph("2. Business Groups", heading_style))

    total_bg = business_groups.count()
    active_bg = business_groups.filter(participation_status='active').count()

    bg_data = [
        ['Metric', 'Value'],
        ['Total Business Groups', str(total_bg)],
        ['Active Groups', str(active_bg)],
    ]

    bg_table = Table(bg_data, colWidths=[3*inch, 2*inch])
    bg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
    ]))
    elements.append(bg_table)
    elements.append(Spacer(1, 20))

    # 3. Savings Groups
    elements.append(Paragraph("3. Savings Groups", heading_style))

    total_sg = savings_groups.count()
    total_savings = savings_groups.aggregate(total=Sum('savings_to_date'))['total'] or 0

    sg_data = [
        ['Metric', 'Value'],
        ['Total Savings Groups', str(total_sg)],
        ['Total Savings (KES)', f"{total_savings:,.2f}"],
    ]

    sg_table = Table(sg_data, colWidths=[3*inch, 2*inch])
    sg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
    ]))
    elements.append(sg_table)
    elements.append(Spacer(1, 20))

    # 4. Mentoring Activities (if applicable)
    if user.is_superuser or user_role in ['me_staff', 'ict_admin', 'field_associate', 'mentor', 'program_manager']:
        elements.append(Paragraph("4. Mentoring Activities", heading_style))

        if user_role == 'mentor' and not user.is_superuser:
            visits = MentoringVisit.objects.filter(mentor=user)
            nudges = PhoneNudge.objects.filter(mentor=user)
        elif user_role == 'field_associate':
            assigned_villages = get_user_assigned_villages(user)
            if assigned_villages:
                visits = MentoringVisit.objects.filter(household__village__in=assigned_villages)
                nudges = PhoneNudge.objects.filter(household__village__in=assigned_villages)
            else:
                visits = MentoringVisit.objects.none()
                nudges = PhoneNudge.objects.none()
        else:
            visits = MentoringVisit.objects.all()
            nudges = PhoneNudge.objects.all()

        thirty_days_ago = timezone.now().date() - timedelta(days=30)

        ma_data = [
            ['Metric', 'Value'],
            ['Total House Visits', str(visits.count())],
            ['Total Phone Calls', str(nudges.count())],
            ['Visits (Last 30 Days)', str(visits.filter(visit_date__gte=thirty_days_ago).count())],
            ['Calls (Last 30 Days)', str(nudges.filter(call_date__gte=thirty_days_ago).count())],
        ]

        ma_table = Table(ma_data, colWidths=[3*inch, 2*inch])
        ma_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ]))
        elements.append(ma_table)

    # Build PDF
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="upg_comprehensive_report_{timezone.now().strftime("%Y%m%d")}.pdf"'

    return response


def _get_pdf_styles():
    """Helper function to get common PDF styles"""
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    custom_styles = {
        'title': ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20, alignment=1),
        'heading': ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#2c3e50')),
        'subheading': ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, spaceAfter=8),
        'normal': styles['Normal'],
    }
    return custom_styles


def _create_summary_table(data, header_color='#3498db'):
    """Helper function to create a styled summary table"""
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle

    table = Table(data, colWidths=[3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    return table


def _create_data_table(data, col_widths=None, header_color='#34495e'):
    """Helper function to create a styled data table"""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    return table


@login_required
def download_household_pdf_report(request):
    """Generate PDF report for households with visualizations"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from io import BytesIO
    from django.db.models import Count

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart
    except ImportError:
        return download_household_report(request)

    households = get_filtered_households(user)
    styles = _get_pdf_styles()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    elements.append(Paragraph("Household Report", styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Paragraph(f"Generated by: {user.get_full_name()}", styles['normal']))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    total = households.count()
    with_phone = households.exclude(phone_number__isnull=True).exclude(phone_number='').count()

    # Get program participation stats
    active_in_programs = HouseholdProgram.objects.filter(
        household__in=households, participation_status='active'
    ).values('household').distinct().count()
    graduated = HouseholdProgram.objects.filter(
        household__in=households, participation_status='graduated'
    ).values('household').distinct().count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Households', str(total)],
        ['With Phone Number', str(with_phone)],
        ['Active in Programs', str(active_in_programs)],
        ['Graduated', str(graduated)],
        ['Phone Coverage', f"{(with_phone/total*100):.1f}%" if total > 0 else '0%'],
    ]
    elements.append(_create_summary_table(summary_data, '#3498db'))
    elements.append(Spacer(1, 20))

    # Distribution by Village (Top 10)
    village_dist = households.values('village__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    if village_dist:
        elements.append(Paragraph("Households by Village (Top 10)", styles['heading']))

        # Create pie chart
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 0
        pie.width = 150
        pie.height = 150
        pie.data = [v['count'] for v in village_dist]
        pie.labels = [v['village__name'][:15] if v['village__name'] else 'Unknown' for v in village_dist]
        pie.slices.strokeWidth = 0.5
        colors_list = [colors.HexColor(c) for c in ['#3498db', '#27ae60', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22', '#2ecc71', '#95a5a6']]
        for i, color in enumerate(colors_list[:len(village_dist)]):
            pie.slices[i].fillColor = color
        drawing.add(pie)
        elements.append(drawing)
        elements.append(Spacer(1, 10))

        # Table
        village_data = [['Village', 'Households', 'Percentage']]
        for v in village_dist:
            pct = (v['count'] / total * 100) if total > 0 else 0
            village_data.append([
                v['village__name'] or 'Unknown',
                str(v['count']),
                f"{pct:.1f}%"
            ])
        elements.append(_create_data_table(village_data, [3*inch, 1.5*inch, 1.5*inch], '#27ae60'))

    elements.append(Spacer(1, 20))

    # Household List (first 50)
    elements.append(PageBreak())
    elements.append(Paragraph("Household Details (First 50)", styles['heading']))

    hh_data = [['Name', 'Village', 'Phone', 'Members']]
    for hh in households.select_related('village').prefetch_related('members')[:50]:
        hh_data.append([
            hh.name[:30],
            hh.village.name[:20] if hh.village else '-',
            hh.phone_number or '-',
            str(hh.members.count())
        ])

    elements.append(_create_data_table(hh_data, [2.5*inch, 2*inch, 1.5*inch, 1*inch]))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="household_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def download_business_groups_pdf_report(request):
    """Generate PDF report for business groups with visualizations"""
    user = request.user

    from io import BytesIO
    from django.db.models import Count

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
    except ImportError:
        return download_business_groups_report(request)

    groups = get_filtered_business_groups(user)
    styles = _get_pdf_styles()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    elements.append(Paragraph("Business Groups Report", styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Spacer(1, 20))

    # Summary
    total = groups.count()
    active = groups.filter(participation_status='active').count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Business Groups', str(total)],
        ['Active Groups', str(active)],
        ['Inactive Groups', str(total - active)],
    ]
    elements.append(_create_summary_table(summary_data, '#27ae60'))
    elements.append(Spacer(1, 20))

    # Distribution by Business Type
    type_dist = groups.values('business_type').annotate(count=Count('id')).order_by('-count')

    if type_dist:
        elements.append(Paragraph("Groups by Business Type", styles['heading']))

        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 0
        pie.width = 150
        pie.height = 150
        pie.data = [t['count'] for t in type_dist]
        pie.labels = [t['business_type'] or 'Other' for t in type_dist]
        colors_list = [colors.HexColor(c) for c in ['#27ae60', '#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']]
        for i, color in enumerate(colors_list[:len(type_dist)]):
            pie.slices[i].fillColor = color
        drawing.add(pie)
        elements.append(drawing)
        elements.append(Spacer(1, 10))

        type_data = [['Business Type', 'Count', 'Percentage']]
        for t in type_dist:
            pct = (t['count'] / total * 100) if total > 0 else 0
            type_data.append([t['business_type'] or 'Other', str(t['count']), f"{pct:.1f}%"])
        elements.append(_create_data_table(type_data, [3*inch, 1.5*inch, 1.5*inch], '#27ae60'))

    elements.append(PageBreak())

    # Group List
    elements.append(Paragraph("Business Group Details (First 50)", styles['heading']))
    bg_data = [['Group Name', 'Business Type', 'Members', 'Status']]
    for g in groups.prefetch_related('members')[:50]:
        bg_data.append([
            g.name[:25],
            g.business_type or '-',
            str(g.members.count()),
            g.participation_status or '-'
        ])
    elements.append(_create_data_table(bg_data, [2.5*inch, 2*inch, 1*inch, 1.5*inch]))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="business_groups_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def download_savings_groups_pdf_report(request):
    """Generate PDF report for savings groups with visualizations"""
    user = request.user

    from io import BytesIO
    from django.db.models import Sum, Count

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        return download_savings_groups_report(request)

    groups = get_filtered_savings_groups(user)
    styles = _get_pdf_styles()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    elements.append(Paragraph("Savings Groups Report", styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Spacer(1, 20))

    # Summary
    total = groups.count()
    active = groups.filter(is_active=True).count()
    total_savings = groups.aggregate(total=Sum('savings_to_date'))['total'] or 0
    total_members = groups.aggregate(total=Count('bsg_members'))['total'] or 0

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Savings Groups', str(total)],
        ['Active Groups', str(active)],
        ['Total Members', str(total_members)],
        ['Total Savings (KES)', f"{total_savings:,.2f}"],
        ['Avg Savings per Group', f"KES {(total_savings/total):,.2f}" if total > 0 else 'KES 0'],
    ]
    elements.append(_create_summary_table(summary_data, '#9b59b6'))
    elements.append(Spacer(1, 20))

    # Group List
    elements.append(Paragraph("Savings Group Details", styles['heading']))
    sg_data = [['Group Name', 'Members', 'Savings (KES)', 'Meeting Day', 'Active']]
    for g in groups.prefetch_related('bsg_members')[:50]:
        sg_data.append([
            g.name[:25],
            str(g.bsg_members.count()),
            f"{g.savings_to_date:,.0f}",
            g.meeting_day or '-',
            'Yes' if g.is_active else 'No'
        ])
    elements.append(_create_data_table(sg_data, [2*inch, 1*inch, 1.5*inch, 1.2*inch, 0.8*inch]))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="savings_groups_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def download_grants_pdf_report(request):
    """Generate PDF report for grants with visualizations"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from io import BytesIO
    from django.db.models import Sum, Count

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart
    except ImportError:
        return download_grants_report(request)

    styles = _get_pdf_styles()

    # Get grants data
    households = get_filtered_households(user)
    business_groups = get_filtered_business_groups(user)

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        sb_grants = SBGrant.objects.all()
        pr_grants = PRGrant.objects.all()
    else:
        from django.db.models import Q
        sb_grants = SBGrant.objects.filter(
            Q(household__in=households) | Q(business_group__in=business_groups)
        )
        pr_grants = PRGrant.objects.filter(
            Q(household__in=households) | Q(business_group__in=business_groups)
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    elements.append(Paragraph("Grants Report", styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Spacer(1, 20))

    # SB Grants Summary
    elements.append(Paragraph("SB Grants Summary", styles['heading']))
    sb_total = sb_grants.count()
    sb_funded = sb_grants.filter(status='disbursed').count()
    sb_amount = sb_grants.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    sb_data = [
        ['Metric', 'Value'],
        ['Total SB Grants', str(sb_total)],
        ['Pending', str(sb_grants.filter(status='pending').count())],
        ['Approved', str(sb_grants.filter(status='approved').count())],
        ['Funded/Disbursed', str(sb_funded)],
        ['Total Amount Disbursed', f"KES {sb_amount:,.0f}"],
    ]
    elements.append(_create_summary_table(sb_data, '#3498db'))
    elements.append(Spacer(1, 20))

    # PR Grants Summary
    elements.append(Paragraph("PR Grants Summary", styles['heading']))
    pr_total = pr_grants.count()
    pr_funded = pr_grants.filter(status='disbursed').count()
    pr_amount = pr_grants.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0

    pr_data = [
        ['Metric', 'Value'],
        ['Total PR Grants', str(pr_total)],
        ['Pending', str(pr_grants.filter(status='pending').count())],
        ['Approved', str(pr_grants.filter(status='approved').count())],
        ['Funded/Disbursed', str(pr_funded)],
        ['Total Amount Disbursed', f"KES {pr_amount:,.0f}"],
    ]
    elements.append(_create_summary_table(pr_data, '#e74c3c'))
    elements.append(Spacer(1, 20))

    # Overall Summary
    elements.append(Paragraph("Overall Grant Summary", styles['heading']))
    overall_data = [
        ['Metric', 'Value'],
        ['Total Grants (All Types)', str(sb_total + pr_total)],
        ['Total Funded', str(sb_funded + pr_funded)],
        ['Total Amount Disbursed', f"KES {(sb_amount + pr_amount):,.0f}"],
    ]
    elements.append(_create_summary_table(overall_data, '#27ae60'))

    # Status distribution chart
    if sb_total > 0 or pr_total > 0:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Grant Status Distribution", styles['heading']))

        drawing = Drawing(400, 180)
        pie = Pie()
        pie.x = 100
        pie.y = 0
        pie.width = 140
        pie.height = 140

        status_counts = {
            'Pending': sb_grants.filter(status='pending').count() + pr_grants.filter(status='pending').count(),
            'Approved': sb_grants.filter(status='approved').count() + pr_grants.filter(status='approved').count(),
            'Funded': sb_funded + pr_funded,
            'Rejected': sb_grants.filter(status='rejected').count() + pr_grants.filter(status='rejected').count(),
        }
        status_counts = {k: v for k, v in status_counts.items() if v > 0}

        pie.data = list(status_counts.values())
        pie.labels = list(status_counts.keys())
        status_colors = {'Pending': '#f39c12', 'Approved': '#3498db', 'Funded': '#27ae60', 'Rejected': '#e74c3c'}
        for i, label in enumerate(status_counts.keys()):
            pie.slices[i].fillColor = colors.HexColor(status_colors.get(label, '#95a5a6'))
        drawing.add(pie)
        elements.append(drawing)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="grants_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def download_training_pdf_report(request):
    """Generate PDF report for training with visualizations"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from io import BytesIO
    from django.db.models import Count

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        return download_training_report(request)

    styles = _get_pdf_styles()
    households = get_filtered_households(user)

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        trainings = Training.objects.all()
    else:
        trainings = Training.objects.filter(
            enrolled_households__household__in=households
        ).distinct()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    elements.append(Paragraph("Training Report", styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Spacer(1, 20))

    # Summary
    total = trainings.count()
    completed = trainings.filter(status='completed').count()
    active = trainings.filter(status='active').count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Trainings', str(total)],
        ['Active', str(active)],
        ['Completed', str(completed)],
        ['Planned', str(trainings.filter(status='planned').count())],
    ]
    elements.append(_create_summary_table(summary_data, '#e67e22'))
    elements.append(Spacer(1, 20))

    # Training List
    elements.append(Paragraph("Training Details", styles['heading']))
    tr_data = [['Training Name', 'Module', 'Status', 'Enrolled', 'Completed']]

    for t in trainings.select_related('bm_cycle').prefetch_related('enrolled_households')[:30]:
        enrolled = t.enrolled_households.count()
        completed_count = t.enrolled_households.filter(enrollment_status='completed').count()
        tr_data.append([
            t.name[:25],
            t.module_id or '-',
            t.status or '-',
            str(enrolled),
            str(completed_count)
        ])

    elements.append(_create_data_table(tr_data, [2.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch]))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="training_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def download_geographic_pdf_report(request):
    """Generate PDF report for geographic analysis with visualizations"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from io import BytesIO
    from django.db.models import Count

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.barcharts import HorizontalBarChart
    except ImportError:
        return download_geographic_report(request)

    from core.models import Village

    styles = _get_pdf_styles()

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        villages = Village.objects.all()
    else:
        assigned_villages = get_user_assigned_villages(user)
        villages = assigned_villages if assigned_villages else Village.objects.none()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    elements.append(Paragraph("Geographic Analysis Report", styles['title']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Spacer(1, 20))

    # Summary
    total_villages = villages.count()
    total_hh = Household.objects.filter(village__in=villages).count()

    elements.append(Paragraph("Summary Statistics", styles['heading']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Villages', str(total_villages)],
        ['Total Households', str(total_hh)],
        ['Avg Households/Village', f"{(total_hh/total_villages):.1f}" if total_villages > 0 else '0'],
    ]
    elements.append(_create_summary_table(summary_data, '#1abc9c'))
    elements.append(Spacer(1, 20))

    # Village breakdown
    elements.append(Paragraph("Households by Village", styles['heading']))
    village_data = [['Village', 'SubCounty', 'Households', 'Active Programs']]

    for v in villages[:30]:
        hh_count = Household.objects.filter(village=v).count()
        active_count = HouseholdProgram.objects.filter(
            household__village=v, participation_status='active'
        ).count()
        village_data.append([
            v.name[:20],
            v.subcounty[:15] if v.subcounty else '-',
            str(hh_count),
            str(active_count)
        ])

    elements.append(_create_data_table(village_data, [2*inch, 1.5*inch, 1.2*inch, 1.3*inch]))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="geographic_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
    return response


# =============================================================================
# Comparative Reports - Compare data across periods (Monthly/Quarterly/Yearly)
# =============================================================================

@login_required
def comparative_report(request):
    """Comparative report builder interface - available to all users"""
    user = request.user
    user_role = getattr(user, 'role', None)

    from core.models import Village

    # Filter villages based on role
    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff', 'county_executive', 'county_assembly']:
        villages = Village.objects.all()
    else:
        assigned_villages = get_user_assigned_villages(user)
        if assigned_villages:
            villages = assigned_villages
        else:
            villages = Village.objects.none()

    # Available comparison types
    comparison_types = [
        ('monthly', 'Monthly Comparison'),
        ('quarterly', 'Quarterly Comparison'),
        ('yearly', 'Yearly Comparison'),
    ]

    # Available metrics to compare
    metrics = [
        ('households', 'Household Registrations'),
        ('enrollments', 'Program Enrollments'),
        ('graduations', 'Program Graduations'),
        ('business_groups', 'Business Groups Formed'),
        ('savings', 'Savings Accumulated'),
        ('grants', 'Grants Disbursed'),
        ('training', 'Training Sessions'),
        ('mentoring', 'Mentoring Activities'),
    ]

    # Get current year for default selection
    current_year = timezone.now().year

    context = {
        'page_title': 'Comparative Reports',
        'villages': villages,
        'comparison_types': comparison_types,
        'metrics': metrics,
        'current_year': current_year,
        'years': list(range(current_year - 5, current_year + 1)),
        'user_role': user_role,
    }

    return render(request, 'reports/comparative_report.html', context)


@login_required
def download_comparative_report(request):
    """Generate comparative report based on user selections"""
    user = request.user
    user_role = getattr(user, 'role', None)

    comparison_type = request.GET.get('comparison_type', 'monthly')
    metric = request.GET.get('metric', 'households')
    year1 = int(request.GET.get('year1', timezone.now().year))
    year2 = int(request.GET.get('year2', timezone.now().year - 1))
    output_format = request.GET.get('output_format', 'pdf')
    village_id = request.GET.get('village')

    # Get comparison data
    data = _get_comparative_data(user, comparison_type, metric, year1, year2, village_id)

    if output_format == 'csv':
        return _generate_comparative_csv(data, comparison_type, metric, year1, year2)
    else:
        return _generate_comparative_pdf(data, comparison_type, metric, year1, year2, user)


def _get_comparative_data(user, comparison_type, metric, year1, year2, village_id=None):
    """Get comparative data for the specified metric and periods"""
    from django.db.models import Sum
    from django.db.models.functions import TruncMonth, TruncQuarter, ExtractMonth, ExtractQuarter
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    # Get filtered base queryset based on user role
    households = get_filtered_households(user)
    if village_id:
        households = households.filter(village_id=village_id)

    data = {
        'metric': metric,
        'comparison_type': comparison_type,
        'year1': year1,
        'year2': year2,
        'periods': [],
        'year1_values': [],
        'year2_values': [],
        'changes': [],
    }

    if comparison_type == 'monthly':
        periods = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data['periods'] = periods

        for month in range(1, 13):
            val1 = _get_metric_value(user, metric, year1, month, None, village_id)
            val2 = _get_metric_value(user, metric, year2, month, None, village_id)
            data['year1_values'].append(val1)
            data['year2_values'].append(val2)

            if val2 > 0:
                change = ((val1 - val2) / val2) * 100
            elif val1 > 0:
                change = 100
            else:
                change = 0
            data['changes'].append(round(change, 1))

    elif comparison_type == 'quarterly':
        periods = ['Q1', 'Q2', 'Q3', 'Q4']
        data['periods'] = periods

        for quarter in range(1, 5):
            val1 = _get_metric_value(user, metric, year1, None, quarter, village_id)
            val2 = _get_metric_value(user, metric, year2, None, quarter, village_id)
            data['year1_values'].append(val1)
            data['year2_values'].append(val2)

            if val2 > 0:
                change = ((val1 - val2) / val2) * 100
            elif val1 > 0:
                change = 100
            else:
                change = 0
            data['changes'].append(round(change, 1))

    elif comparison_type == 'yearly':
        # Compare multiple years
        years = list(range(min(year1, year2), max(year1, year2) + 1))
        data['periods'] = [str(y) for y in years]
        data['year1_values'] = []
        data['year2_values'] = []  # Not used for yearly

        for year in years:
            val = _get_metric_value(user, metric, year, None, None, village_id)
            data['year1_values'].append(val)

        # Calculate year-over-year changes
        for i in range(len(data['year1_values'])):
            if i == 0:
                data['changes'].append(0)
            else:
                prev = data['year1_values'][i - 1]
                curr = data['year1_values'][i]
                if prev > 0:
                    change = ((curr - prev) / prev) * 100
                elif curr > 0:
                    change = 100
                else:
                    change = 0
                data['changes'].append(round(change, 1))

    # Calculate totals
    data['year1_total'] = sum(data['year1_values'])
    data['year2_total'] = sum(data['year2_values']) if data['year2_values'] else 0

    if data['year2_total'] > 0:
        data['total_change'] = round(((data['year1_total'] - data['year2_total']) / data['year2_total']) * 100, 1)
    elif data['year1_total'] > 0:
        data['total_change'] = 100
    else:
        data['total_change'] = 0

    return data


def _get_metric_value(user, metric, year, month=None, quarter=None, village_id=None):
    """Get the value for a specific metric in a given period"""
    from django.db.models import Sum, Count
    from datetime import datetime

    # Build date range
    if month:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    elif quarter:
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3 + 1
        start_date = datetime(year, start_month, 1)
        if end_month > 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, end_month, 1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

    # Make timezone aware
    start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
    end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

    # Get filtered queryset based on user role
    households = get_filtered_households(user)
    if village_id:
        households = households.filter(village_id=village_id)
    household_ids = list(households.values_list('id', flat=True))

    if metric == 'households':
        return Household.objects.filter(
            id__in=household_ids,
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()

    elif metric == 'enrollments':
        return HouseholdProgram.objects.filter(
            household_id__in=household_ids,
            enrollment_date__gte=start_date.date(),
            enrollment_date__lt=end_date.date()
        ).count()

    elif metric == 'graduations':
        return HouseholdProgram.objects.filter(
            household_id__in=household_ids,
            participation_status='graduated',
            graduation_date__gte=start_date.date(),
            graduation_date__lt=end_date.date()
        ).count()

    elif metric == 'business_groups':
        return BusinessGroup.objects.filter(
            members__household_id__in=household_ids,
            formation_date__gte=start_date.date(),
            formation_date__lt=end_date.date()
        ).distinct().count()

    elif metric == 'savings':
        total = BusinessSavingsGroup.objects.filter(
            bsg_members__household_id__in=household_ids,
            formation_date__gte=start_date.date(),
            formation_date__lt=end_date.date()
        ).aggregate(total=Sum('savings_to_date'))['total']
        return int(total or 0)

    elif metric == 'grants':
        sb_count = SBGrant.objects.filter(
            business_group__members__household_id__in=household_ids,
            disbursement_date__gte=start_date.date(),
            disbursement_date__lt=end_date.date(),
            status='disbursed'
        ).distinct().count()
        pr_count = PRGrant.objects.filter(
            business_group__members__household_id__in=household_ids,
            disbursement_date__gte=start_date.date(),
            disbursement_date__lt=end_date.date(),
            status='disbursed'
        ).distinct().count()
        return sb_count + pr_count

    elif metric == 'training':
        return Training.objects.filter(
            enrolled_households__household_id__in=household_ids,
            start_date__gte=start_date.date(),
            start_date__lt=end_date.date()
        ).distinct().count()

    elif metric == 'mentoring':
        visits = MentoringVisit.objects.filter(
            household_id__in=household_ids,
            visit_date__gte=start_date.date(),
            visit_date__lt=end_date.date()
        ).count()
        calls = PhoneNudge.objects.filter(
            household_id__in=household_ids,
            call_date__gte=start_date.date(),
            call_date__lt=end_date.date()
        ).count()
        return visits + calls

    return 0


def _generate_comparative_csv(data, comparison_type, metric, year1, year2):
    """Generate CSV for comparative report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="comparative_{metric}_{comparison_type}_{year1}_vs_{year2}.csv"'

    writer = csv.writer(response)

    metric_labels = {
        'households': 'Household Registrations',
        'enrollments': 'Program Enrollments',
        'graduations': 'Program Graduations',
        'business_groups': 'Business Groups Formed',
        'savings': 'Savings Accumulated (KES)',
        'grants': 'Grants Disbursed',
        'training': 'Training Sessions',
        'mentoring': 'Mentoring Activities',
    }

    writer.writerow([f'Comparative Report: {metric_labels.get(metric, metric)}'])
    writer.writerow([f'Comparison Type: {comparison_type.title()}'])
    writer.writerow([])

    if comparison_type == 'yearly':
        writer.writerow(['Year', 'Value', 'Change (%)'])
        for i, period in enumerate(data['periods']):
            writer.writerow([period, data['year1_values'][i], f"{data['changes'][i]}%"])
    else:
        writer.writerow(['Period', str(year1), str(year2), 'Change (%)'])
        for i, period in enumerate(data['periods']):
            writer.writerow([
                period,
                data['year1_values'][i],
                data['year2_values'][i],
                f"{data['changes'][i]}%"
            ])

    writer.writerow([])
    writer.writerow(['Total', data['year1_total'], data.get('year2_total', ''), f"{data['total_change']}%"])

    return response


def _generate_comparative_pdf(data, comparison_type, metric, year1, year2, user):
    """Generate PDF for comparative report with charts"""
    from io import BytesIO

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.graphics.shapes import Drawing, String
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.linecharts import HorizontalLineChart
        from reportlab.graphics.charts.legends import Legend
    except ImportError:
        return _generate_comparative_csv(data, comparison_type, metric, year1, year2)

    styles = _get_pdf_styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    metric_labels = {
        'households': 'Household Registrations',
        'enrollments': 'Program Enrollments',
        'graduations': 'Program Graduations',
        'business_groups': 'Business Groups Formed',
        'savings': 'Savings Accumulated (KES)',
        'grants': 'Grants Disbursed',
        'training': 'Training Sessions',
        'mentoring': 'Mentoring Activities',
    }

    # Title
    title = f"Comparative Report: {metric_labels.get(metric, metric)}"
    elements.append(Paragraph(title, styles['title']))

    if comparison_type == 'yearly':
        subtitle = f"Yearly Trend Analysis ({data['periods'][0]} - {data['periods'][-1]})"
    else:
        subtitle = f"{comparison_type.title()} Comparison: {year1} vs {year2}"
    elements.append(Paragraph(subtitle, styles['normal']))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y at %H:%M')}", styles['normal']))
    elements.append(Paragraph(f"Generated by: {user.get_full_name() or user.username}", styles['normal']))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    elements.append(Paragraph("Summary", styles['heading']))

    if comparison_type == 'yearly':
        summary_data = [
            ['Metric', 'Value'],
            ['Total (All Years)', f"{data['year1_total']:,}"],
            ['Average per Year', f"{data['year1_total'] // len(data['periods']):,}"],
            ['Highest Year', f"{data['periods'][data['year1_values'].index(max(data['year1_values']))]} ({max(data['year1_values']):,})"],
            ['Lowest Year', f"{data['periods'][data['year1_values'].index(min(data['year1_values']))]} ({min(data['year1_values']):,})"],
        ]
    else:
        summary_data = [
            ['Metric', 'Value'],
            [f'Total {year1}', f"{data['year1_total']:,}"],
            [f'Total {year2}', f"{data['year2_total']:,}"],
            ['Change', f"{data['total_change']:+.1f}%"],
            ['Trend', 'Increasing' if data['total_change'] > 0 else 'Decreasing' if data['total_change'] < 0 else 'Stable'],
        ]

    elements.append(_create_summary_table(summary_data, '#2c3e50'))
    elements.append(Spacer(1, 20))

    # Bar Chart Comparison
    elements.append(Paragraph("Visual Comparison", styles['heading']))

    drawing = Drawing(700, 250)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 180
    bc.width = 600

    if comparison_type == 'yearly':
        bc.data = [data['year1_values']]
        bc.bars[0].fillColor = colors.HexColor('#3498db')
    else:
        bc.data = [data['year1_values'], data['year2_values']]
        bc.bars[0].fillColor = colors.HexColor('#3498db')
        bc.bars[1].fillColor = colors.HexColor('#e74c3c')

    bc.categoryAxis.categoryNames = data['periods']
    bc.categoryAxis.labels.fontName = 'Helvetica'
    bc.categoryAxis.labels.fontSize = 8

    bc.valueAxis.valueMin = 0
    max_val = max(max(data['year1_values']), max(data['year2_values']) if data['year2_values'] else 0)
    bc.valueAxis.valueMax = max_val * 1.2 if max_val > 0 else 10
    bc.valueAxis.valueStep = max(1, int(max_val / 5))

    drawing.add(bc)

    # Add legend
    if comparison_type != 'yearly':
        legend = Legend()
        legend.x = 550
        legend.y = 230
        legend.colorNamePairs = [
            (colors.HexColor('#3498db'), str(year1)),
            (colors.HexColor('#e74c3c'), str(year2)),
        ]
        drawing.add(legend)

    elements.append(drawing)
    elements.append(Spacer(1, 20))

    # Data Table
    elements.append(Paragraph("Detailed Data", styles['heading']))

    if comparison_type == 'yearly':
        table_data = [['Period', 'Value', 'Change (%)']]
        for i, period in enumerate(data['periods']):
            change_str = f"{data['changes'][i]:+.1f}%" if data['changes'][i] != 0 else "—"
            table_data.append([period, f"{data['year1_values'][i]:,}", change_str])
        table_data.append(['TOTAL', f"{data['year1_total']:,}", f"{data['total_change']:+.1f}%"])
        col_widths = [2*inch, 2*inch, 2*inch]
    else:
        table_data = [['Period', str(year1), str(year2), 'Difference', 'Change (%)']]
        for i, period in enumerate(data['periods']):
            diff = data['year1_values'][i] - data['year2_values'][i]
            diff_str = f"{diff:+,}" if diff != 0 else "0"
            change_str = f"{data['changes'][i]:+.1f}%" if data['changes'][i] != 0 else "—"
            table_data.append([
                period,
                f"{data['year1_values'][i]:,}",
                f"{data['year2_values'][i]:,}",
                diff_str,
                change_str
            ])
        total_diff = data['year1_total'] - data['year2_total']
        table_data.append([
            'TOTAL',
            f"{data['year1_total']:,}",
            f"{data['year2_total']:,}",
            f"{total_diff:+,}",
            f"{data['total_change']:+.1f}%"
        ])
        col_widths = [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comparative_{metric}_{comparison_type}_{year1}_vs_{year2}.pdf"'
    return response
