"""
Grant Application and Review Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from households.models import Household
from programs.models import Program
from .models import (HouseholdGrantApplication, SBGrant, PRGrant,
                     GrantProgram, GrantFieldAssociate, GrantMentorAssignment)
from decimal import Decimal
import json
from itertools import chain
from operator import attrgetter
from django.contrib.auth import get_user_model

User = get_user_model()


def _get_user_households(user):
    """
    Get households accessible to the user based on their role and assigned villages.
    Users only see households in their directly assigned villages.
    """
    if user.role in ['mentor', 'field_associate'] and hasattr(user, 'profile') and user.profile:
        assigned_villages = user.profile.assigned_villages.all()
        if assigned_villages.exists():
            return Household.objects.filter(
                village__in=assigned_villages
            ).select_related('village')
        return Household.objects.none()

    # Admin roles - show all households
    if user.role in ['ict_admin', 'program_manager', 'me_staff'] or user.is_superuser:
        return Household.objects.all().select_related('village')

    return Household.objects.none()


@login_required
def grant_application_list(request):
    """List all grant applications (Household, SB, PR) with filtering by status and grant type"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Get Household grants based on role and assignments
    if user_role == 'mentor':
        # Mentors only see grants they submitted on behalf of households
        household_grants = HouseholdGrantApplication.objects.filter(
            submitted_by=user
        ).select_related('household', 'household__village', 'program', 'grant_program', 'approved_by', 'reviewed_by', 'submitted_by')

    elif user_role == 'field_associate':
        # FA sees grants for households in their assigned villages
        assigned_villages = user.profile.assigned_villages.all() if hasattr(user, 'profile') and user.profile else []
        household_grants = HouseholdGrantApplication.objects.filter(
            Q(household__village__in=assigned_villages) |
            Q(submitted_by=user)
        ).select_related('household', 'household__village', 'program', 'grant_program', 'approved_by', 'reviewed_by', 'submitted_by')

    elif user_role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff'] or user.is_superuser:
        household_grants = HouseholdGrantApplication.objects.all().select_related('household', 'household__village', 'program', 'grant_program', 'approved_by', 'reviewed_by', 'submitted_by')
    else:
        household_grants = HouseholdGrantApplication.objects.none()

    # Get SB and PR grants
    if user_role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff', 'field_associate'] or user.is_superuser:
        sb_grants = SBGrant.objects.all().select_related('business_group', 'program')
        pr_grants = PRGrant.objects.all().select_related('business_group', 'program', 'sb_grant')
    elif user_role == 'mentor':
        # Mentors see SB/PR grants they submitted
        sb_grants = SBGrant.objects.filter(submitted_by=user).select_related('business_group', 'program')
        pr_grants = PRGrant.objects.none()
    else:
        sb_grants = SBGrant.objects.none()
        pr_grants = PRGrant.objects.none()

    # Apply filters
    status_filter = request.GET.get('status')
    grant_type_filter = request.GET.get('grant_type')
    funding_source_filter = request.GET.get('funding_source')

    if status_filter:
        household_grants = household_grants.filter(status=status_filter)
        sb_grants = sb_grants.filter(status=status_filter)
        pr_grants = pr_grants.filter(status=status_filter)

    # Filter by funding source (grant_program vs program)
    if funding_source_filter == 'grant_program':
        household_grants = household_grants.filter(grant_program__isnull=False)
        sb_grants = SBGrant.objects.none()
        pr_grants = PRGrant.objects.none()
    elif funding_source_filter == 'program':
        household_grants = household_grants.filter(grant_program__isnull=True, program__isnull=False)
        sb_grants = SBGrant.objects.none()
        pr_grants = PRGrant.objects.none()

    if grant_type_filter:
        if grant_type_filter == 'sb':
            household_grants = HouseholdGrantApplication.objects.none()
            pr_grants = PRGrant.objects.none()
        elif grant_type_filter == 'pr':
            household_grants = HouseholdGrantApplication.objects.none()
            sb_grants = SBGrant.objects.none()
        else:
            # Household grant type filter
            household_grants = household_grants.filter(grant_type=grant_type_filter)
            sb_grants = SBGrant.objects.none()
            pr_grants = PRGrant.objects.none()

    # Add grant type attribute to each grant for display
    for grant in household_grants:
        if grant.grant_program:
            grant.display_type = f'{grant.grant_program.name}'
            grant.funding_source = 'Grant Program'
        elif grant.program:
            grant.display_type = f'{grant.program.name} - {grant.get_grant_type_display()}'
            grant.funding_source = 'Program'
        else:
            grant.display_type = f'Household - {grant.get_grant_type_display()}'
            grant.funding_source = 'General'
        grant.grant_category = 'household'

    for grant in sb_grants:
        grant.display_type = 'SB Grant'
        grant.grant_category = 'sb'
        grant.funding_source = 'SB Grant'

    for grant in pr_grants:
        grant.display_type = 'PR Grant'
        grant.grant_category = 'pr'
        grant.funding_source = 'PR Grant'

    # Combine all grants and sort by creation date
    all_grants = sorted(
        chain(household_grants, sb_grants, pr_grants),
        key=attrgetter('created_at'),
        reverse=True
    )

    # Determine user permissions
    # FA and Mentors can apply for beneficiaries, PM and ICT can create grant programs
    can_create = user_role in ['mentor', 'field_associate', 'program_manager', 'ict_admin'] or user.is_superuser
    can_create_program = user_role in ['program_manager', 'ict_admin'] or user.is_superuser
    can_review = user_role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff'] or user.is_superuser
    can_approve = user_role in ['program_manager', 'county_director', 'executive', 'ict_admin'] or user.is_superuser

    # Create comprehensive grant type choices
    grant_type_choices = [
        ('sb', 'SB Grant'),
        ('pr', 'PR Grant'),
    ] + list(HouseholdGrantApplication.GRANT_TYPE_CHOICES)

    # Get available grants for mentors and field associates
    available_grants = None
    if user_role in ['mentor', 'field_associate']:
        active_programs = Program.objects.filter(status='active')
        available_grants = {
            'programs': active_programs,
            'grant_types': HouseholdGrantApplication.GRANT_TYPE_CHOICES,
        }

    context = {
        'applications': all_grants,
        'page_title': 'All Grant Applications',
        'can_create': can_create,
        'can_create_program': can_create_program,
        'can_review': can_review,
        'can_approve': can_approve,
        'status_filter': status_filter,
        'grant_type_filter': grant_type_filter,
        'status_choices': HouseholdGrantApplication.STATUS_CHOICES,
        'grant_type_choices': grant_type_choices,
        'available_grants': available_grants,
        'user_role': user_role,
    }
    return render(request, 'upg_grants/application_list.html', context)


@login_required
def grant_application_create(request, household_id=None):
    """Create a new grant application for household, business group, or savings group
    FA and Mentors can apply for beneficiaries assigned to them
    """
    user = request.user

    # Check permissions - FA and Mentors can apply for beneficiaries, admin roles can too
    if user.role not in ['mentor', 'field_associate', 'ict_admin', 'me_staff', 'program_manager'] and not user.is_superuser:
        messages.error(request, 'You do not have permission to create grant applications.')
        return redirect('dashboard:dashboard')

    # Handle both URL parameter and GET parameters
    applicant_type = request.GET.get('applicant_type')
    applicant_id = request.GET.get('applicant_id')
    grant_type_param = request.GET.get('grant_type')
    grant_program_id = request.GET.get('grant_program')

    household = None
    business_group = None
    savings_group = None
    applicant_name = ""
    selected_grant_program = None

    # Get grant program if specified
    if grant_program_id:
        from upg_grants.models import GrantProgram
        try:
            selected_grant_program = GrantProgram.objects.get(id=grant_program_id, status='active')
        except GrantProgram.DoesNotExist:
            pass

    # If called with household_id (old style)
    if household_id:
        household = get_object_or_404(Household, id=household_id)
        applicant_name = household.name
    # New style with GET parameters
    elif applicant_type and applicant_id:
        from business_groups.models import BusinessGroup
        from savings_groups.models import BusinessSavingsGroup

        if applicant_type == 'household':
            household = get_object_or_404(Household, id=applicant_id)
            applicant_name = household.name
        elif applicant_type == 'business_group':
            business_group = get_object_or_404(BusinessGroup, id=applicant_id)
            applicant_name = business_group.name
        elif applicant_type == 'savings_group':
            savings_group = get_object_or_404(BusinessSavingsGroup, id=applicant_id)
            applicant_name = savings_group.name
    # If only grant_type or grant_program is provided, show household selection page
    elif grant_type_param or (selected_grant_program and not applicant_id):
        # Get households for mentor/field associate
        households = _get_user_households(user)

        # Get available grant programs for selection
        active_grant_programs = GrantProgram.objects.filter(status='active')

        context = {
            'households': households,
            'grant_type': grant_type_param,
            'grant_programs': active_grant_programs,
            'selected_grant_program': selected_grant_program,
            'page_title': f'Select Household for {selected_grant_program.name if selected_grant_program else "Grant"} Application',
        }
        return render(request, 'upg_grants/select_household.html', context)
    else:
        # If nothing specified, show household selection with all active grants
        households = _get_user_households(user)

        from upg_grants.models import GrantProgram
        active_grant_programs = GrantProgram.objects.filter(status='active')

        context = {
            'households': households,
            'grant_programs': active_grant_programs,
            'page_title': 'Apply for Grant - Select Household',
        }
        return render(request, 'upg_grants/select_household.html', context)

    if request.method == 'POST':
        grant_type = request.POST.get('grant_type')
        requested_amount = Decimal(request.POST.get('requested_amount', 0))
        title = request.POST.get('title')
        purpose = request.POST.get('purpose')
        business_plan = request.POST.get('business_plan', '')
        expected_outcomes = request.POST.get('expected_outcomes')
        program_id = request.POST.get('program')
        grant_program_id = request.POST.get('grant_program')

        # Parse budget breakdown from form
        budget_items = request.POST.getlist('budget_item[]')
        budget_amounts = request.POST.getlist('budget_amount[]')
        budget_breakdown = {}
        for item, amount in zip(budget_items, budget_amounts):
            if item and amount:
                budget_breakdown[item] = float(amount)

        # Handle funding source - either program or grant_program
        program = None
        selected_gp = None
        if grant_program_id:
            # If grant program is selected, use its program and grant_type
            try:
                selected_gp = GrantProgram.objects.get(id=grant_program_id)
                program = selected_gp.program
                grant_type = selected_gp.grant_type  # Override with grant program's type
            except GrantProgram.DoesNotExist:
                pass
        elif program_id:
            program = get_object_or_404(Program, id=program_id)

        application = HouseholdGrantApplication.objects.create(
            household=household,
            business_group=business_group,
            savings_group=savings_group,
            submitted_by=user,
            program=program,
            grant_program=selected_gp,  # Link to the grant program
            grant_type=grant_type,
            requested_amount=requested_amount,
            title=title,
            purpose=purpose,
            business_plan=business_plan,
            expected_outcomes=expected_outcomes,
            budget_breakdown=budget_breakdown,
            status='submitted',
            submission_date=timezone.now()
        )

        messages.success(request, f'Grant application "{title}" submitted successfully!')
        return redirect('upg_grants:application_detail', application_id=application.id)

    programs = Program.objects.filter(status='active')
    grant_programs = GrantProgram.objects.filter(status='active')

    context = {
        'household': household,
        'business_group': business_group,
        'savings_group': savings_group,
        'applicant_name': applicant_name,
        'programs': programs,
        'grant_programs': grant_programs,
        'selected_grant_program': selected_grant_program,
        'page_title': f'Apply for Grant - {applicant_name}',
        'preselected_grant_type': grant_type_param,  # Pre-fill grant type from URL
    }
    return render(request, 'upg_grants/application_create.html', context)


@login_required
def grant_application_detail(request, application_id):
    """View details of a grant application"""
    application = get_object_or_404(HouseholdGrantApplication, id=application_id)

    context = {
        'application': application,
        'can_review': application.can_be_reviewed_by(request.user),
        'can_approve': application.can_be_approved_by(request.user),
        'page_title': f'Grant Application - {application.title}',
    }
    return render(request, 'upg_grants/application_detail.html', context)


@login_required
def grant_application_review(request, application_id):
    """Review interface for grant applications"""
    application = get_object_or_404(HouseholdGrantApplication, id=application_id)

    if not application.can_be_reviewed_by(request.user):
        messages.error(request, 'You do not have permission to review this application.')
        return redirect('upg_grants:application_detail', application_id=application_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'review':
            application.status = 'under_review'
            application.reviewed_by = request.user
            application.review_date = timezone.now()
            application.review_notes = request.POST.get('review_notes', '')
            application.review_score = int(request.POST.get('review_score', 0)) if request.POST.get('review_score') else None
            application.save()
            messages.success(request, 'Application marked as under review.')

        elif action == 'approve' and application.can_be_approved_by(request.user):
            application.status = 'approved'
            application.approved_by = request.user
            application.approval_date = timezone.now()
            application.approval_notes = request.POST.get('approval_notes', '')
            application.approved_amount = Decimal(request.POST.get('approved_amount', application.requested_amount))
            application.save()
            messages.success(request, 'Application approved successfully!')

        elif action == 'reject' and application.can_be_approved_by(request.user):
            application.status = 'rejected'
            application.approved_by = request.user
            application.approval_date = timezone.now()
            application.approval_notes = request.POST.get('approval_notes', '')
            application.save()
            messages.warning(request, 'Application rejected.')

        return redirect('upg_grants:application_detail', application_id=application_id)

    context = {
        'application': application,
        'can_review': application.can_be_reviewed_by(request.user),
        'can_approve': application.can_be_approved_by(request.user),
        'page_title': f'Review Application - {application.title}',
    }
    return render(request, 'upg_grants/application_review.html', context)


@login_required
def pending_reviews(request):
    """List of applications pending review for managers"""
    user = request.user

    # Allow anyone who can access grants to view pending reviews
    if not (user.is_superuser or user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff', 'field_associate', 'mentor']):
        messages.error(request, 'You do not have permission to view pending grant reviews.')
        return redirect('grants:grants_dashboard')

    pending_applications = HouseholdGrantApplication.objects.filter(
        Q(status='submitted') | Q(status='under_review')
    ).select_related('household', 'program', 'submitted_by', 'reviewed_by').order_by('-submission_date')

    # Determine if user can review applications
    can_review = user.is_superuser or user.role in ['program_manager', 'county_director', 'executive', 'ict_admin', 'me_staff']

    context = {
        'applications': pending_applications,
        'page_title': 'Pending Grant Reviews',
        'can_review': can_review,
    }
    return render(request, 'upg_grants/pending_reviews.html', context)


@login_required
def available_grants_list(request):
    """List all available open grants for application"""
    user = request.user

    # Check permissions - mentors and field associates can apply for grants
    if user.role not in ['mentor', 'field_associate', 'ict_admin', 'me_staff']:
        messages.error(request, 'You do not have permission to view available grants.')
        return redirect('dashboard:dashboard')

    # Get all active programs for grant opportunities
    active_programs = Program.objects.filter(status='active')

    # For household grants, these are always available for application
    grant_types = HouseholdGrantApplication.GRANT_TYPE_CHOICES

    context = {
        'active_programs': active_programs,
        'grant_types': grant_types,
        'page_title': 'Available Grants',
    }
    return render(request, 'upg_grants/available_grants.html', context)


# ========== Grant Program Management (PM Only) ==========

@login_required
def grant_program_list(request):
    """List all grant programs - PM sees all, FA/Mentor see assigned only"""
    user = request.user
    user_role = getattr(user, 'role', None)

    if user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff']:
        # Admin roles see all grant programs
        grant_programs = GrantProgram.objects.all().select_related('program', 'created_by')
        can_create = user_role in ['program_manager', 'ict_admin'] or user.is_superuser
    elif user_role in ['field_associate', 'mentor']:
        # FA and Mentors see all active grant programs so they can apply on behalf of households
        grant_programs = GrantProgram.objects.filter(status='active').select_related('program', 'created_by')
        can_create = False
    else:
        messages.error(request, 'You do not have permission to view grant programs.')
        return redirect('dashboard:dashboard')

    # Get field associates for assignment (PM only)
    field_associates = []
    if can_create:
        field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')

    context = {
        'grant_programs': grant_programs,
        'page_title': 'Grant Programs',
        'can_create': can_create,
        'field_associates': field_associates,
        'programs': Program.objects.filter(status='active'),
        'grant_type_choices': HouseholdGrantApplication.GRANT_TYPE_CHOICES,
        'user_role': user_role,
    }
    return render(request, 'upg_grants/grant_program_list.html', context)


@login_required
def grant_program_create(request):
    """Create a new grant program - PM and ICT Admin only"""
    user = request.user

    # Only PM and ICT Admin can create grant programs
    if not (user.is_superuser or user.role in ['program_manager', 'ict_admin']):
        messages.error(request, 'Only Program Managers and ICT Admin can create grant programs.')
        return redirect('upg_grants:grant_program_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        grant_type = request.POST.get('grant_type')
        program_id = request.POST.get('program')
        total_budget = Decimal(request.POST.get('total_budget', 0))
        max_amount = Decimal(request.POST.get('max_amount_per_beneficiary', 15000))
        min_amount = Decimal(request.POST.get('min_amount_per_beneficiary', 5000))
        application_start = request.POST.get('application_start_date') or None
        application_end = request.POST.get('application_end_date') or None
        status = request.POST.get('status', 'draft')
        fa_ids = request.POST.getlist('field_associates[]') or request.POST.getlist('field_associates')

        program = None
        if program_id:
            program = get_object_or_404(Program, id=program_id)

        grant_program = GrantProgram.objects.create(
            name=name,
            description=description,
            grant_type=grant_type,
            program=program,
            total_budget=total_budget,
            max_amount_per_beneficiary=max_amount,
            min_amount_per_beneficiary=min_amount,
            application_start_date=application_start,
            application_end_date=application_end,
            status=status,
            created_by=user
        )

        # Assign Field Associates
        for fa_id in fa_ids:
            try:
                fa_user = User.objects.get(id=fa_id, role='field_associate')
                GrantFieldAssociate.objects.create(
                    grant_program=grant_program,
                    field_associate=fa_user,
                    assigned_by=user,
                    status='pending'
                )
            except User.DoesNotExist:
                pass

        messages.success(request, f'Grant program "{name}" created successfully!')
        return redirect('upg_grants:grant_program_list')

    # GET request
    field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')
    programs = Program.objects.filter(status='active')

    context = {
        'page_title': 'Create Grant Program',
        'field_associates': field_associates,
        'programs': programs,
        'grant_type_choices': HouseholdGrantApplication.GRANT_TYPE_CHOICES,
    }
    return render(request, 'upg_grants/grant_program_create.html', context)


@login_required
def grant_program_detail(request, grant_program_id):
    """View grant program details"""
    grant_program = get_object_or_404(GrantProgram, id=grant_program_id)
    user = request.user

    # Check access
    has_access = (
        user.is_superuser or
        user.role in ['ict_admin', 'program_manager', 'me_staff'] or
        GrantFieldAssociate.objects.filter(grant_program=grant_program, field_associate=user).exists() or
        GrantMentorAssignment.objects.filter(grant_fa__grant_program=grant_program, mentor=user).exists()
    )

    if not has_access:
        messages.error(request, 'You do not have access to this grant program.')
        return redirect('upg_grants:grant_program_list')

    # Get FA assignments
    fa_assignments = GrantFieldAssociate.objects.filter(
        grant_program=grant_program
    ).select_related('field_associate', 'assigned_by')

    # Get applications for this grant program (directly linked via grant_program field)
    applications = HouseholdGrantApplication.objects.filter(
        grant_program=grant_program
    ).select_related('household', 'submitted_by', 'reviewed_by', 'approved_by')

    context = {
        'grant_program': grant_program,
        'fa_assignments': fa_assignments,
        'applications': applications,
        'page_title': f'Grant Program - {grant_program.name}',
        'can_edit': user.is_superuser or user.role in ['program_manager', 'ict_admin'],
        'can_assign_mentors': user.role == 'field_associate',
    }
    return render(request, 'upg_grants/grant_program_detail.html', context)


@login_required
def grant_assign_mentors(request, grant_program_id):
    """FA assigns mentors to a grant program"""
    grant_program = get_object_or_404(GrantProgram, id=grant_program_id)
    user = request.user

    # Check if user is FA assigned to this grant program
    try:
        fa_assignment = GrantFieldAssociate.objects.get(
            grant_program=grant_program,
            field_associate=user
        )
    except GrantFieldAssociate.DoesNotExist:
        # Allow admin roles too
        if not (user.is_superuser or user.role in ['me_staff', 'ict_admin', 'program_manager']):
            messages.error(request, 'You are not assigned to manage this grant program.')
            return redirect('upg_grants:grant_program_list')
        fa_assignment = None

    if request.method == 'POST':
        mentor_ids = request.POST.getlist('mentors[]') or request.POST.getlist('mentors')

        if fa_assignment:
            # Get current mentor assignments
            current_mentor_ids = set(GrantMentorAssignment.objects.filter(
                grant_fa=fa_assignment
            ).values_list('mentor_id', flat=True))

            new_mentor_ids = set(int(m_id) for m_id in mentor_ids if m_id)

            # Add new mentors
            added_count = 0
            for mentor_id in new_mentor_ids - current_mentor_ids:
                try:
                    mentor = User.objects.get(id=mentor_id, role='mentor')
                    GrantMentorAssignment.objects.create(
                        grant_fa=fa_assignment,
                        mentor=mentor,
                        assigned_by=user
                    )
                    added_count += 1
                except User.DoesNotExist:
                    pass

            # Remove unselected mentors
            removed_count = GrantMentorAssignment.objects.filter(
                grant_fa=fa_assignment,
                mentor_id__in=(current_mentor_ids - new_mentor_ids)
            ).delete()[0]

            messages.success(request, f'Mentor assignments updated. Added: {added_count}, Removed: {removed_count}')

        return redirect('upg_grants:grant_assign_mentors', grant_program_id=grant_program_id)

    # GET request
    # Get available mentors
    if user.role == 'field_associate' and hasattr(user, 'profile') and user.profile:
        available_mentors = list(user.profile.supervised_mentors)
    else:
        available_mentors = list(User.objects.filter(role='mentor', is_active=True))

    # Get assigned mentors
    assigned_mentor_ids = []
    if fa_assignment:
        assigned_mentor_ids = list(GrantMentorAssignment.objects.filter(
            grant_fa=fa_assignment
        ).values_list('mentor_id', flat=True))

    context = {
        'grant_program': grant_program,
        'fa_assignment': fa_assignment,
        'available_mentors': available_mentors,
        'assigned_mentor_ids': assigned_mentor_ids,
        'page_title': f'Assign Mentors - {grant_program.name}',
    }
    return render(request, 'upg_grants/grant_assign_mentors.html', context)


@login_required
def grant_fa_assignments_list(request):
    """List grant programs assigned to the current FA"""
    user = request.user

    if user.role != 'field_associate':
        messages.error(request, 'This page is for Field Associates only.')
        return redirect('upg_grants:grant_program_list')

    fa_assignments = GrantFieldAssociate.objects.filter(
        field_associate=user
    ).select_related('grant_program', 'assigned_by')

    context = {
        'fa_assignments': fa_assignments,
        'page_title': 'My Grant Assignments',
    }
    return render(request, 'upg_grants/grant_fa_assignments_list.html', context)
