"""
Excel Export Views for UPG System Reports

These views provide Excel download endpoints for various report types.
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from core.permissions import can_access_module
from .excel_export import (
    export_households_excel,
    export_business_groups_excel,
    export_savings_groups_excel,
    export_grants_excel,
    export_training_excel,
    export_comprehensive_report,
    create_single_sheet_excel
)


@login_required
def download_households_excel(request):
    """Export households report as Excel."""
    if not can_access_module(request.user, 'reports'):
        messages.error(request, 'You do not have permission to export reports.')
        return redirect('dashboard:dashboard')

    from households.models import Household
    from core.permissions import filter_queryset_by_village

    queryset = Household.objects.select_related(
        'village',
        'village__subcounty_obj',
        'village__subcounty_obj__county'
    ).prefetch_related('members')

    # Apply geographic filters
    queryset = filter_queryset_by_village(queryset, request.user)

    # Apply date filters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')

    if start_date:
        queryset = queryset.filter(enrollment_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(enrollment_date__lte=end_date)
    if status:
        queryset = queryset.filter(status=status)

    return export_households_excel(queryset, f"Household Report - {timezone.now().strftime('%Y-%m-%d')}")


@login_required
def download_business_groups_excel(request):
    """Export business groups report as Excel."""
    if not can_access_module(request.user, 'reports'):
        messages.error(request, 'You do not have permission to export reports.')
        return redirect('dashboard:dashboard')

    from business_groups.models import BusinessGroup

    queryset = BusinessGroup.objects.prefetch_related('members', 'members__household')

    # Apply filters from request
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)

    return export_business_groups_excel(queryset, f"Business Groups Report - {timezone.now().strftime('%Y-%m-%d')}")


@login_required
def download_savings_groups_excel(request):
    """Export savings groups report as Excel."""
    if not can_access_module(request.user, 'reports'):
        messages.error(request, 'You do not have permission to export reports.')
        return redirect('dashboard:dashboard')

    from savings_groups.models import BusinessSavingsGroup

    queryset = BusinessSavingsGroup.objects.prefetch_related('members')

    # Apply filters from request
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)

    return export_savings_groups_excel(queryset, f"Savings Groups Report - {timezone.now().strftime('%Y-%m-%d')}")


@login_required
def download_grants_excel(request):
    """Export grants report as Excel."""
    if not can_access_module(request.user, 'reports'):
        messages.error(request, 'You do not have permission to export reports.')
        return redirect('dashboard:dashboard')

    from upg_grants.models import GrantApplication

    queryset = GrantApplication.objects.select_related(
        'grant_program',
        'household'
    ).order_by('-created_at')

    # Apply filters from request
    status = request.GET.get('status')
    grant_type = request.GET.get('grant_type')

    if status:
        queryset = queryset.filter(status=status)
    if grant_type:
        queryset = queryset.filter(grant_program__grant_type=grant_type)

    return export_grants_excel(queryset, f"Grants Report - {timezone.now().strftime('%Y-%m-%d')}")


@login_required
def download_training_excel(request):
    """Export training sessions report as Excel."""
    if not can_access_module(request.user, 'reports'):
        messages.error(request, 'You do not have permission to export reports.')
        return redirect('dashboard:dashboard')

    from training.models import TrainingSession

    queryset = TrainingSession.objects.select_related(
        'training_module',
        'facilitator'
    ).prefetch_related('attendees').order_by('-date')

    # Apply filters from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    return export_training_excel(queryset, f"Training Report - {timezone.now().strftime('%Y-%m-%d')}")


@login_required
def download_comprehensive_excel(request):
    """Export comprehensive multi-sheet Excel report."""
    if not can_access_module(request.user, 'reports'):
        messages.error(request, 'You do not have permission to export reports.')
        return redirect('dashboard:dashboard')

    from households.models import Household
    from business_groups.models import BusinessGroup
    from savings_groups.models import BusinessSavingsGroup
    from upg_grants.models import GrantApplication
    from training.models import TrainingSession
    from core.permissions import filter_queryset_by_village

    data_dict = {}

    # Households Sheet
    households = Household.objects.select_related(
        'village',
        'village__subcounty_obj',
        'village__subcounty_obj__county'
    )
    households = filter_queryset_by_village(households, request.user)

    household_headers = ['Household ID', 'Head of Household', 'National ID', 'Phone', 'Village', 'SubCounty', 'Status', 'Enrollment Date']
    household_rows = []
    for hh in households[:1000]:  # Limit to 1000 for performance
        household_rows.append([
            hh.household_id,
            hh.head_of_household,
            hh.national_id,
            hh.phone_number,
            hh.village.name if hh.village else '',
            hh.village.subcounty_obj.name if hh.village and hh.village.subcounty_obj else '',
            hh.status,
            hh.enrollment_date.strftime('%Y-%m-%d') if hh.enrollment_date else ''
        ])
    data_dict['Households'] = {'headers': household_headers, 'rows': household_rows}

    # Business Groups Sheet
    bgroups = BusinessGroup.objects.prefetch_related('members')
    bg_headers = ['ID', 'Group Name', 'Registration No', 'Status', 'Formation Date', 'Members Count']
    bg_rows = []
    for bg in bgroups[:500]:
        bg_rows.append([
            bg.id,
            bg.name,
            bg.registration_number or '',
            bg.status,
            bg.formation_date.strftime('%Y-%m-%d') if bg.formation_date else '',
            bg.members.count()
        ])
    data_dict['Business Groups'] = {'headers': bg_headers, 'rows': bg_rows}

    # Savings Groups Sheet
    sgroups = BusinessSavingsGroup.objects.prefetch_related('members')
    sg_headers = ['ID', 'Group Name', 'Status', 'Formation Date', 'Members Count', 'Total Savings']
    sg_rows = []
    for sg in sgroups[:500]:
        sg_rows.append([
            sg.id,
            sg.name,
            getattr(sg, 'status', ''),
            sg.formation_date.strftime('%Y-%m-%d') if hasattr(sg, 'formation_date') and sg.formation_date else '',
            sg.members.count(),
            getattr(sg, 'total_savings', 0)
        ])
    data_dict['Savings Groups'] = {'headers': sg_headers, 'rows': sg_rows}

    # Grants Sheet
    grants = GrantApplication.objects.select_related('grant_program', 'household')[:500]
    grants_headers = ['ID', 'Grant Type', 'Applicant', 'Status', 'Amount Requested', 'Amount Approved', 'Date']
    grants_rows = []
    for g in grants:
        grants_rows.append([
            g.id,
            g.grant_program.name if g.grant_program else '',
            g.household.head_of_household if g.household else '',
            g.status,
            getattr(g, 'amount_requested', 0),
            getattr(g, 'amount_approved', 0),
            g.created_at.strftime('%Y-%m-%d') if g.created_at else ''
        ])
    data_dict['Grants'] = {'headers': grants_headers, 'rows': grants_rows}

    # Training Sheet
    training = TrainingSession.objects.select_related('training_module', 'facilitator')[:500]
    training_headers = ['ID', 'Module', 'Date', 'Facilitator', 'Attendees', 'Status']
    training_rows = []
    for t in training:
        training_rows.append([
            t.id,
            t.training_module.name if t.training_module else '',
            t.date.strftime('%Y-%m-%d') if t.date else '',
            t.facilitator.get_full_name() if t.facilitator else '',
            t.attendees.count() if hasattr(t, 'attendees') else 0,
            getattr(t, 'status', '')
        ])
    data_dict['Training'] = {'headers': training_headers, 'rows': training_rows}

    return export_comprehensive_report(
        data_dict,
        f"UPG Comprehensive Report - {timezone.now().strftime('%Y-%m-%d')}"
    )
