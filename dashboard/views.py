"""
Dashboard Views for UPG System
Enhanced with visualizations borrowed from UPG Kaduna MIS
"""

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

# Try to import dateutil, fall back to manual calculation if not available
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Simple fallback for relativedelta
    class relativedelta:
        def __init__(self, months=0):
            self.months = months

        def __rsub__(self, other):
            # Approximate month subtraction
            year = other.year
            month = other.month - self.months
            while month <= 0:
                month += 12
                year -= 1
            day = min(other.day, 28)  # Safe day for all months
            return other.replace(year=year, month=month, day=day)
from households.models import Household, HouseholdProgram
from business_groups.models import BusinessGroup
from upg_grants.models import SBGrant, PRGrant, HouseholdGrantApplication
from savings_groups.models import BusinessSavingsGroup
from training.models import Training, MentoringVisit, PhoneNudge, MentoringReport, HouseholdTrainingEnrollment
from core.models import BusinessMentorCycle
from core.services import DataQualityService


# =============================================================================
# Dashboard Helper Functions (Borrowed from UPG Kaduna MIS patterns)
# =============================================================================

def get_enrollment_trend(months=6, village_ids=None):
    """
    Get enrollment trend for the last N months.
    Returns data formatted for Chart.js line chart.
    """
    labels = []
    values = []

    # Get data for the last N months
    for i in range(months - 1, -1, -1):
        month_date = timezone.now().date() - relativedelta(months=i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

        queryset = Household.objects.filter(
            created_at__date__lte=month_end
        )
        if village_ids:
            queryset = queryset.filter(village_id__in=village_ids)

        count = queryset.count()
        labels.append(month_date.strftime('%b %Y'))
        values.append(count)

    return {
        'labels': json.dumps(labels),
        'values': json.dumps(values)
    }


def get_status_distribution(village_ids=None):
    """
    Get household participation status distribution.
    Returns data formatted for Chart.js doughnut chart.
    """
    queryset = HouseholdProgram.objects.all()
    if village_ids:
        queryset = queryset.filter(household__village_id__in=village_ids)

    status_counts = queryset.values('participation_status').annotate(
        count=Count('id')
    ).order_by('participation_status')

    # Map status values to display labels
    status_labels = {
        'active': 'Active',
        'graduated': 'Graduated',
        'dropout': 'Dropout',
        'suspended': 'Suspended',
        'pending': 'Pending'
    }

    labels = []
    values = []
    colors = []

    color_map = {
        'active': 'rgba(40, 167, 69, 0.8)',      # Green
        'graduated': 'rgba(23, 162, 184, 0.8)',  # Cyan
        'dropout': 'rgba(220, 53, 69, 0.8)',     # Red
        'suspended': 'rgba(255, 193, 7, 0.8)',   # Yellow
        'pending': 'rgba(108, 117, 125, 0.8)'    # Gray
    }

    for item in status_counts:
        status = item['participation_status']
        labels.append(status_labels.get(status, status.title()))
        values.append(item['count'])
        colors.append(color_map.get(status, 'rgba(54, 162, 235, 0.8)'))

    return {
        'labels': json.dumps(labels),
        'values': json.dumps(values),
        'colors': json.dumps(colors)
    }


def get_geographic_distribution(village_ids=None):
    """
    Get household distribution by subcounty/village.
    Returns data formatted for Chart.js horizontal bar chart.
    """
    queryset = Household.objects.all()
    if village_ids:
        queryset = queryset.filter(village_id__in=village_ids)

    # Group by subcounty
    by_subcounty = queryset.values(
        'village__subcounty_obj__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    labels = []
    values = []

    for item in by_subcounty:
        name = item['village__subcounty_obj__name'] or 'Unassigned'
        labels.append(name)
        values.append(item['count'])

    return {
        'labels': json.dumps(labels),
        'values': json.dumps(values)
    }


def get_grant_distribution():
    """
    Get grant distribution by type.
    Returns data for bar chart.
    """
    sb_count = SBGrant.objects.filter(status='disbursed').count()
    pr_count = PRGrant.objects.filter(status='disbursed').count()
    household_count = HouseholdGrantApplication.objects.filter(status='disbursed').count()

    return {
        'labels': json.dumps(['SB Grants', 'PR Grants', 'Household Grants']),
        'values': json.dumps([sb_count, pr_count, household_count]),
        'colors': json.dumps([
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(75, 192, 192, 0.8)'
        ])
    }


def get_dashboard_alerts(user=None, village_ids=None):
    """
    Get actionable alerts for dashboard.
    Returns list of alert objects with severity and action URLs.
    """
    alerts = []
    thirty_days_ago = timezone.now().date() - timedelta(days=30)

    # Alert 1: Pending grant applications
    pending_grants_query = HouseholdGrantApplication.objects.filter(
        status__in=['submitted', 'under_review']
    )
    if village_ids:
        pending_grants_query = pending_grants_query.filter(
            household__village_id__in=village_ids
        )
    pending_grants = pending_grants_query.count()

    if pending_grants > 0:
        alerts.append({
            'type': 'pending_grants',
            'count': pending_grants,
            'title': 'Pending Grant Applications',
            'description': 'Applications awaiting review or approval',
            'severity': 'warning',
            'icon': 'fa-clock',
            'action_url': reverse('upg_grants:application_list') + '?status=pending',
            'action_text': 'Review'
        })

    # Alert 2: Households without program enrollment
    no_program_query = Household.objects.filter(
        program_participations__isnull=True
    )
    if village_ids:
        no_program_query = no_program_query.filter(village_id__in=village_ids)
    no_program = no_program_query.count()

    if no_program > 0:
        alerts.append({
            'type': 'no_program',
            'count': no_program,
            'title': 'Households Not Enrolled',
            'description': 'Households registered but not enrolled in any program',
            'severity': 'info',
            'icon': 'fa-user-plus',
            'action_url': reverse('households:household_list') + '?filter=no_program',
            'action_text': 'Enroll'
        })

    # Alert 3: Overdue mentoring visits (no visit in 30+ days for active households)
    if user and hasattr(user, 'role') and user.role == 'mentor':
        overdue_visits = Household.objects.filter(
            village__in=village_ids if village_ids else [],
            program_participations__participation_status='active'
        ).exclude(
            mentoring_visits__visit_date__gte=thirty_days_ago
        ).count() if village_ids else 0

        if overdue_visits > 0:
            alerts.append({
                'type': 'overdue_visits',
                'count': overdue_visits,
                'title': 'Overdue Mentoring Visits',
                'description': 'Active households not visited in 30+ days',
                'severity': 'danger',
                'icon': 'fa-exclamation-triangle',
                'action_url': reverse('training:visit_list'),
                'action_text': 'Schedule'
            })

    return alerts


def calculate_kpis(village_ids=None):
    """
    Calculate KPIs with target tracking.
    Returns dict of KPI data for display.
    """
    # These targets would typically come from a ProgramTarget model
    # For now, using reasonable defaults

    queryset = Household.objects.all()
    program_queryset = HouseholdProgram.objects.all()

    if village_ids:
        queryset = queryset.filter(village_id__in=village_ids)
        program_queryset = program_queryset.filter(household__village_id__in=village_ids)

    total_enrolled = queryset.count()
    active_count = program_queryset.filter(participation_status='active').count()
    graduated_count = program_queryset.filter(participation_status='graduated').count()

    # Example targets (would be configurable in production)
    enrollment_target = max(total_enrolled, 1000)  # Dynamic or configured
    graduation_target = max(int(total_enrolled * 0.7), 100)  # 70% graduation goal

    return {
        'enrollment': {
            'value': total_enrolled,
            'target': enrollment_target,
            'title': 'Total Enrollment',
            'icon': 'fa-users',
            'icon_bg': 'primary-subtle',
            'icon_color': 'primary'
        },
        'active': {
            'value': active_count,
            'target': None,  # No target, just tracking
            'title': 'Active Households',
            'icon': 'fa-house-user',
            'icon_bg': 'success-subtle',
            'icon_color': 'success'
        },
        'graduated': {
            'value': graduated_count,
            'target': graduation_target,
            'title': 'Graduated',
            'icon': 'fa-graduation-cap',
            'icon_bg': 'info-subtle',
            'icon_color': 'info'
        },
        'grants_disbursed': {
            'value': (
                SBGrant.objects.filter(status='disbursed').count() +
                PRGrant.objects.filter(status='disbursed').count() +
                HouseholdGrantApplication.objects.filter(status='disbursed').count()
            ),
            'target': None,
            'title': 'Grants Disbursed',
            'icon': 'fa-hand-holding-usd',
            'icon_bg': 'warning-subtle',
            'icon_color': 'warning'
        }
    }


@login_required
def dashboard_view(request):
    """Role-based dashboard routing"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Route to specific dashboard based on role
    # Hierarchy: Admin/ICT -> PM -> M&E -> Field Associate -> Mentor
    if user.is_superuser or user_role == 'ict_admin':
        return admin_dashboard_view(request)
    elif user_role == 'program_manager':
        return pm_dashboard_view(request)
    elif user_role == 'mentor':
        return mentor_dashboard_view(request)
    elif user_role in ['county_executive', 'county_assembly']:
        return executive_dashboard_view(request)
    elif user_role in ['me_staff', 'cco_director']:
        return me_dashboard_view(request)
    elif user_role == 'field_associate':
        return field_associate_dashboard_view(request)
    else:
        return general_dashboard_view(request)


@login_required
def admin_dashboard_view(request):
    """System Administrator dashboard view - Enhanced with visualizations"""
    user = request.user

    # Program Overview Statistics
    total_households = Household.objects.count()
    graduated_count = HouseholdProgram.objects.filter(participation_status='graduated').count()
    graduation_rate = round(graduated_count / total_households * 100, 1) if total_households > 0 else 0

    program_overview = {
        'total_households_enrolled': total_households,
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),
        'graduation_rate': graduation_rate,
        'program_completion_status': f'{graduation_rate}%'
    }

    # Geographic Coverage - Updated to use subcounty_obj
    geographic_coverage = {
        'villages_by_county': Household.objects.values('village__subcounty_obj').distinct().count(),
        'household_distribution': Household.objects.count(),
        'mentor_coverage_map': 'West Pokot Focus',
        'saturation_levels': '42%'
    }

    # Financial Metrics - Calculate total disbursed from all grant types
    sb_disbursed = SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0
    pr_disbursed = PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0
    household_disbursed = HouseholdGrantApplication.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    # Calculate actual total savings from all savings groups
    total_savings = BusinessSavingsGroup.objects.filter(is_active=True).aggregate(
        total=Sum('savings_to_date')
    )['total'] or 0

    financial_metrics = {
        'grants_disbursed': sb_disbursed + pr_disbursed + household_disbursed,
        'business_progress': BusinessGroup.objects.filter(participation_status='active').count(),
        'savings_accumulated': total_savings,
        'income_generation': '125%'
    }

    # Training Progress
    training_progress = {
        'modules_completed': Training.objects.filter(status='completed').count(),
        'attendance_rates': '89%',
        'skill_development': 'High',
        'mentoring_sessions': MentoringVisit.objects.count()
    }

    # Basic statistics for existing cards - Include all grant types
    stats = {
        'total_households': total_households,
        'active_households': HouseholdProgram.objects.filter(participation_status='active').count(),
        'graduated_households': graduated_count,
        'total_business_groups': BusinessGroup.objects.count(),
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),
        'total_savings_groups': BusinessSavingsGroup.objects.filter(is_active=True).count(),
        'sb_grants_funded': SBGrant.objects.filter(status='disbursed').count(),
        'pr_grants_funded': PRGrant.objects.filter(status='disbursed').count(),
        'household_grants_funded': HouseholdGrantApplication.objects.filter(status='disbursed').count(),
        'total_grants_funded': (
            SBGrant.objects.filter(status='disbursed').count() +
            PRGrant.objects.filter(status='disbursed').count() +
            HouseholdGrantApplication.objects.filter(status='disbursed').count()
        ),
        # Mentor activity logs for admin - Use current month
        'total_house_visits': MentoringVisit.objects.count(),
        'total_phone_calls': PhoneNudge.objects.count(),
        'visits_this_month': MentoringVisit.objects.filter(
            visit_date__gte=timezone.now().date().replace(day=1)
        ).count(),
        'calls_this_month': PhoneNudge.objects.filter(
            call_date__gte=timezone.now().date().replace(day=1)
        ).count(),
    }

    # Role-specific data
    if user.role == 'mentor':
        # Mentor sees only their assigned villages/households
        if hasattr(user, 'profile') and user.profile:
            try:
                assigned_villages = user.profile.assigned_villages
                # Check if it's a QuerySet or Manager
                if hasattr(assigned_villages, 'all'):
                    stats['assigned_villages'] = assigned_villages.count()
                elif assigned_villages is not None:
                    # It's a list or other iterable
                    stats['assigned_villages'] = len(assigned_villages)
                else:
                    stats['assigned_villages'] = 0
            except (AttributeError, TypeError):
                stats['assigned_villages'] = 0
        else:
            stats['assigned_villages'] = 0

    elif user.role in ['county_executive', 'county_assembly']:
        # County-level users see high-level summaries
        pass

    elif user.role in ['me_staff', 'cco_director']:
        # M&E and directors see all data
        pass

    # =========================================================================
    # NEW: Enhanced Dashboard Data (Borrowed from UPG Kaduna MIS)
    # =========================================================================

    # Chart Data
    enrollment_trend = get_enrollment_trend(months=6)
    status_distribution = get_status_distribution()
    geographic_distribution = get_geographic_distribution()
    grant_distribution = get_grant_distribution()

    # KPIs with targets
    kpis = calculate_kpis()

    # Alerts
    alerts = get_dashboard_alerts(user=user)

    # Data Quality
    data_quality = DataQualityService.get_quality_report()

    context = {
        'user': user,
        'stats': stats,
        'program_overview': program_overview,
        'geographic_coverage': geographic_coverage,
        'financial_metrics': financial_metrics,
        'training_progress': training_progress,
        # New enhanced data
        'enrollment_trend': enrollment_trend,
        'status_distribution': status_distribution,
        'geographic_distribution': geographic_distribution,
        'grant_distribution': grant_distribution,
        'kpis': kpis,
        'alerts': alerts,
        'data_quality': data_quality,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def mentor_dashboard_view(request):
    """Mentor-specific dashboard with training assignments"""
    user = request.user

    # Get mentor's assigned trainings
    assigned_trainings = Training.objects.filter(assigned_mentor=user).order_by('-start_date')

    # Get current/active trainings (includes trainings without end_date)
    from django.db.models import Q
    current_date = timezone.now().date()
    current_trainings = assigned_trainings.filter(
        Q(status__in=['planned', 'active']) &
        Q(start_date__lte=current_date) &
        (Q(end_date__gte=current_date) | Q(end_date__isnull=True))
    )

    # Get households in mentor's assigned villages (more comprehensive)
    # Ensure profile exists (defensive coding for edge cases)
    from accounts.models import UserProfile
    try:
        profile = user.profile
    except (AttributeError, UserProfile.DoesNotExist):
        # Create profile if it doesn't exist
        profile, _ = UserProfile.objects.get_or_create(user=user)

    assigned_villages = []
    if profile:
        try:
            assigned_villages = profile.assigned_villages.all()
        except (AttributeError, TypeError):
            # Handle case where assigned_villages might be a list instead of QuerySet
            assigned_villages = getattr(profile, 'assigned_villages', [])
            if not hasattr(assigned_villages, 'all'):
                assigned_villages = list(assigned_villages) if assigned_villages else []

    if assigned_villages:
        mentor_households = Household.objects.filter(village__in=assigned_villages).distinct()
    else:
        # Fallback to households in mentor's trainings
        mentor_households = Household.objects.filter(
            current_training_enrollment__training__assigned_mentor=user
        ).distinct()

    # Date ranges - Current month for accurate "this month" counts
    today = timezone.now().date()
    month_start = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)

    # Current month activities for stats
    month_visits = MentoringVisit.objects.filter(
        mentor=user,
        visit_date__gte=month_start
    ).order_by('-visit_date')

    month_nudges = PhoneNudge.objects.filter(
        mentor=user,
        call_date__gte=month_start
    ).order_by('-call_date')

    # Recent activities (last 30 days) for display
    recent_visits = MentoringVisit.objects.filter(
        mentor=user,
        visit_date__gte=thirty_days_ago
    ).order_by('-visit_date')

    recent_nudges = PhoneNudge.objects.filter(
        mentor=user,
        call_date__gte=thirty_days_ago
    ).order_by('-call_date')

    # Grant statistics for mentor's households
    mentor_grant_applications = HouseholdGrantApplication.objects.filter(
        household__in=mentor_households
    ).select_related('household', 'program')

    grant_stats = {
        'total_applications': mentor_grant_applications.count(),
        'applied': mentor_grant_applications.filter(status__in=['submitted', 'draft']).count(),
        'under_review': mentor_grant_applications.filter(status='under_review').count(),
        'approved': mentor_grant_applications.filter(status='approved').count(),
        'disbursed': mentor_grant_applications.filter(status='disbursed').count(),
        'rejected': mentor_grant_applications.filter(status='rejected').count(),
    }

    # Recent grant applications (last 5)
    recent_grants = mentor_grant_applications.order_by('-created_at')[:5]

    # Stats for mentor dashboard - Use month counts for accurate "this month" stats
    stats = {
        'assigned_trainings': assigned_trainings.count(),
        'active_trainings': current_trainings.count(),
        'total_households': mentor_households.count(),
        'visits_this_month': month_visits.count(),
        'nudges_this_month': month_nudges.count(),
        'pending_reports': 0,  # Can be calculated based on reporting schedule
        'total_grant_applications': grant_stats['total_applications'],
    }

    # Upcoming activities (next 7 days)
    upcoming_trainings = assigned_trainings.filter(
        start_date__gte=timezone.now().date(),
        start_date__lte=timezone.now().date() + timedelta(days=7)
    )

    # Get village IDs for the mentor
    village_ids = None
    if assigned_villages:
        if hasattr(assigned_villages, 'values_list'):
            village_ids = list(assigned_villages.values_list('id', flat=True))
        else:
            village_ids = [v.id for v in assigned_villages] if assigned_villages else None

    # Enhanced: Data quality for mentor's villages
    data_quality = DataQualityService.get_quality_report(village_ids)

    # Enhanced: Alerts for mentor
    alerts = get_dashboard_alerts(user=user, village_ids=village_ids)

    # Enhanced: Progress indicators
    total_households_count = mentor_households.count() if mentor_households else 0
    visited_this_month = month_visits.count()
    visit_target = max(total_households_count, 1)  # At least visit each household once

    progress_indicators = {
        'household_visits': {
            'label': 'Household Visits This Month',
            'current': visited_this_month,
            'target': visit_target,
        },
        'grant_applications': {
            'label': 'Grant Applications',
            'current': grant_stats['disbursed'],
            'target': grant_stats['total_applications'] or 1,
        }
    }

    context = {
        'user': user,
        'stats': stats,
        'assigned_trainings': assigned_trainings[:5],  # Latest 5
        'current_trainings': current_trainings,
        'mentor_households': mentor_households,  # All assigned households
        'recent_visits': recent_visits[:5],
        'recent_nudges': recent_nudges[:5],
        'upcoming_trainings': upcoming_trainings,
        'grant_stats': grant_stats,
        'recent_grants': recent_grants,
        'dashboard_type': 'mentor',
        # Enhanced data
        'data_quality': data_quality,
        'alerts': alerts,
        'progress_indicators': progress_indicators,
    }

    return render(request, 'dashboard/mentor_dashboard.html', context)


@login_required
def executive_dashboard_view(request):
    """County Executive dashboard with high-level metrics"""
    user = request.user

    # High-level statistics - Include all grant types
    sb_disbursed = SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0
    pr_disbursed = PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0
    household_disbursed = HouseholdGrantApplication.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    total_households = Household.objects.count()
    graduated_count = HouseholdProgram.objects.filter(participation_status='graduated').count()
    graduation_rate = round(graduated_count / total_households * 100, 1) if total_households > 0 else 0

    stats = {
        'total_households': total_households,
        'active_households': HouseholdProgram.objects.filter(participation_status='active').count(),
        'graduated_households': graduated_count,
        'graduation_rate': graduation_rate,
        'total_trainings': Training.objects.count(),
        'active_mentors': Training.objects.values('assigned_mentor').distinct().count(),
        'grants_disbursed': sb_disbursed + pr_disbursed + household_disbursed,
        'total_grants_funded': (
            SBGrant.objects.filter(status='disbursed').count() +
            PRGrant.objects.filter(status='disbursed').count() +
            HouseholdGrantApplication.objects.filter(status='disbursed').count()
        ),
        'total_business_groups': BusinessGroup.objects.count(),
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),
    }

    # Enhanced: KPIs for executive view
    kpis = calculate_kpis()

    # Enhanced: Chart data
    enrollment_trend = get_enrollment_trend(months=6)
    status_distribution = get_status_distribution()
    geographic_distribution = get_geographic_distribution()
    grant_distribution = get_grant_distribution()

    context = {
        'user': user,
        'stats': stats,
        'dashboard_type': 'executive',
        # Enhanced data
        'kpis': kpis,
        'enrollment_trend': enrollment_trend,
        'status_distribution': status_distribution,
        'geographic_distribution': geographic_distribution,
        'grant_distribution': grant_distribution,
    }

    return render(request, 'dashboard/executive_dashboard.html', context)


@login_required
def me_dashboard_view(request):
    """M&E Staff dashboard with monitoring data"""
    user = request.user

    # Get date ranges - Use current month for "this month" counts
    today = timezone.now().date()
    month_start = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # Monitoring & Evaluation specific metrics - Use current month
    stats = {
        'total_reports': MentoringReport.objects.count(),
        'pending_reports': MentoringReport.objects.filter(
            submitted_date__gte=month_start
        ).count(),
        'training_completion_rate': 0,  # Calculate based on training completion
        'household_visits': MentoringVisit.objects.filter(
            visit_date__gte=month_start
        ).count(),
        'phone_nudges': PhoneNudge.objects.filter(
            call_date__gte=month_start
        ).count(),
        'total_mentor_activities': MentoringVisit.objects.count() + PhoneNudge.objects.count(),
        'recent_visits': MentoringVisit.objects.filter(
            visit_date__gte=seven_days_ago
        ).count(),
        'recent_calls': PhoneNudge.objects.filter(
            call_date__gte=seven_days_ago
        ).count(),
    }

    # Recent mentor activities (current month) - combining visits and calls
    recent_visits = MentoringVisit.objects.filter(
        visit_date__gte=month_start
    ).select_related('household', 'mentor', 'household__village').order_by('-visit_date')[:10]

    recent_calls = PhoneNudge.objects.filter(
        call_date__gte=month_start
    ).select_related('household', 'mentor', 'household__village').order_by('-call_date')[:10]

    # Staff activity summary - Include all users who recorded visits (Mentors, FAs, PMs)
    from django.db.models import Count
    staff_activity = []
    from accounts.models import User

    # Get all users who have recorded any visits or calls this month
    users_with_visits = MentoringVisit.objects.filter(
        visit_date__gte=month_start
    ).values_list('mentor_id', flat=True).distinct()

    users_with_calls = PhoneNudge.objects.filter(
        call_date__gte=month_start
    ).values_list('mentor_id', flat=True).distinct()

    active_user_ids = set(users_with_visits) | set(users_with_calls)
    active_users = User.objects.filter(id__in=active_user_ids, is_active=True)

    for staff in active_users:
        visit_count = MentoringVisit.objects.filter(
            mentor=staff,
            visit_date__gte=month_start
        ).count()
        call_count = PhoneNudge.objects.filter(
            mentor=staff,
            call_date__gte=month_start
        ).count()
        staff_activity.append({
            'mentor': staff,
            'visits': visit_count,
            'calls': call_count,
            'total': visit_count + call_count,
            'role': staff.get_role_display() if hasattr(staff, 'get_role_display') else staff.role
        })

    # Sort by total activity
    staff_activity.sort(key=lambda x: x['total'], reverse=True)
    mentor_activity = staff_activity  # Keep variable name for template compatibility

    # Enhanced: Data quality report for M&E
    data_quality = DataQualityService.get_quality_report()

    # Enhanced: Chart data for M&E
    enrollment_trend = get_enrollment_trend(months=6)
    status_distribution = get_status_distribution()

    context = {
        'user': user,
        'stats': stats,
        'recent_visits': recent_visits,
        'recent_calls': recent_calls,
        'mentor_activity': mentor_activity[:10],  # Top 10 most active mentors
        'dashboard_type': 'me',
        # Enhanced data
        'data_quality': data_quality,
        'enrollment_trend': enrollment_trend,
        'status_distribution': status_distribution,
    }

    return render(request, 'dashboard/me_dashboard.html', context)


@login_required
def pm_dashboard_view(request):
    """
    Program Manager dashboard - Program-focused view
    PM supervises Field Associates who supervise Mentors
    Hierarchy: PM -> Field Associate -> Mentor
    """
    user = request.user
    from accounts.models import User

    # Get all Field Associates and Mentors under PM's supervision
    field_associates = User.objects.filter(role='field_associate', is_active=True)
    mentors = User.objects.filter(role='mentor', is_active=True)

    # Date ranges - Use current month for "this month" counts
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Program Overview Statistics
    total_households = Household.objects.count()
    graduated_count = HouseholdProgram.objects.filter(participation_status='graduated').count()
    graduation_rate = round(graduated_count / total_households * 100, 1) if total_households > 0 else 0

    # Grant statistics
    sb_disbursed = SBGrant.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0
    pr_disbursed = PRGrant.objects.filter(status='disbursed').aggregate(total=Sum('grant_amount'))['total'] or 0
    household_disbursed = HouseholdGrantApplication.objects.filter(status='disbursed').aggregate(total=Sum('disbursed_amount'))['total'] or 0

    stats = {
        # Program metrics
        'total_households': total_households,
        'active_households': HouseholdProgram.objects.filter(participation_status='active').count(),
        'graduated_households': graduated_count,
        'graduation_rate': graduation_rate,

        # Team metrics
        'total_field_associates': field_associates.count(),
        'total_mentors': mentors.count(),
        'total_team_size': field_associates.count() + mentors.count(),

        # Business & Grants
        'total_business_groups': BusinessGroup.objects.count(),
        'active_business_groups': BusinessGroup.objects.filter(participation_status='active').count(),
        'total_grants_disbursed': sb_disbursed + pr_disbursed + household_disbursed,
        'grants_count': (
            SBGrant.objects.filter(status='disbursed').count() +
            PRGrant.objects.filter(status='disbursed').count() +
            HouseholdGrantApplication.objects.filter(status='disbursed').count()
        ),

        # Training metrics
        'total_trainings': Training.objects.count(),
        'active_trainings': Training.objects.filter(status='active').count(),
        'completed_trainings': Training.objects.filter(status='completed').count(),

        # Savings groups
        'total_savings_groups': BusinessSavingsGroup.objects.filter(is_active=True).count(),

        # Activity metrics (this month)
        'visits_this_month': MentoringVisit.objects.filter(visit_date__gte=month_start).count(),
        'calls_this_month': PhoneNudge.objects.filter(call_date__gte=month_start).count(),
    }

    # Field Associate Performance Summary
    # FA supervises mentors -> mentors have villages -> villages have households
    fa_performance = []
    for fa in field_associates:
        # Get mentors supervised by this FA
        fa_mentors = User.objects.filter(
            role='mentor',
            is_active=True,
            profile__supervisor=fa
        )

        # Get all villages from those mentors
        fa_village_ids = []
        for mentor in fa_mentors:
            if hasattr(mentor, 'profile') and mentor.profile:
                mentor_villages = list(mentor.profile.assigned_villages.values_list('id', flat=True))
                fa_village_ids.extend(mentor_villages)
        fa_village_ids = list(set(fa_village_ids))  # Remove duplicates

        # Count households in those villages
        fa_households = Household.objects.filter(village_id__in=fa_village_ids).count() if fa_village_ids else 0

        # Count mentoring activities by FA's mentors (this month)
        fa_visits = MentoringVisit.objects.filter(
            mentor__in=fa_mentors,
            visit_date__gte=month_start
        ).count()

        fa_calls = PhoneNudge.objects.filter(
            mentor__in=fa_mentors,
            call_date__gte=month_start
        ).count()

        fa_performance.append({
            'user': fa,
            'name': fa.get_full_name() or fa.username,
            'mentors': fa_mentors.count(),
            'households': fa_households,
            'villages': len(fa_village_ids),
            'visits_this_month': fa_visits,
            'calls_this_month': fa_calls,
            'total_activity': fa_visits + fa_calls,
        })

    # Sort by total activity (most active first)
    fa_performance.sort(key=lambda x: x['total_activity'], reverse=True)

    # Program Progress - Milestones overview
    from households.models import UPGMilestone
    milestone_stats = UPGMilestone.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        overdue=Count('id', filter=Q(
            status__in=['not_started', 'in_progress'],
            target_date__lt=timezone.now().date()
        ))
    )

    # Recent grant applications
    pending_grants = HouseholdGrantApplication.objects.filter(
        status__in=['submitted', 'under_review']
    ).select_related('household', 'program').order_by('-created_at')[:5]

    # Chart data
    enrollment_trend = get_enrollment_trend(months=6)
    status_distribution = get_status_distribution()
    geographic_distribution = get_geographic_distribution()
    grant_distribution = get_grant_distribution()

    # KPIs
    kpis = calculate_kpis()

    # Alerts for PM
    alerts = get_dashboard_alerts(user=user)

    context = {
        'user': user,
        'stats': stats,
        'fa_performance': fa_performance[:10],  # Top 10 Field Associates
        'field_associates': field_associates,
        'mentors': mentors,
        'milestone_stats': milestone_stats,
        'pending_grants': pending_grants,
        'dashboard_type': 'program_manager',
        # Chart data
        'enrollment_trend': enrollment_trend,
        'status_distribution': status_distribution,
        'geographic_distribution': geographic_distribution,
        'grant_distribution': grant_distribution,
        'kpis': kpis,
        'alerts': alerts,
    }

    return render(request, 'dashboard/pm_dashboard.html', context)


@login_required
def field_associate_dashboard_view(request):
    """
    Field Associate dashboard with mentor oversight

    Hierarchy: PM -> FA -> Mentor -> Villages -> Households
    - FA supervises mentors (mentor.profile.supervisor = FA)
    - Mentors have assigned_villages
    - FA sees all villages from their supervised mentors
    - FA sees all households in those villages
    """
    user = request.user
    from accounts.models import User
    from core.models import Village

    # Get mentors supervised by this Field Associate
    # Mentors where profile.supervisor = this FA
    supervised_mentors = User.objects.filter(
        role='mentor',
        is_active=True,
        profile__supervisor=user
    ).select_related('profile')

    # Get ALL villages from supervised mentors (not FA's own villages)
    # Villages are assigned to mentors, FA sees villages through their mentors
    village_ids = []
    all_villages = Village.objects.none()

    for mentor in supervised_mentors:
        if hasattr(mentor, 'profile') and mentor.profile:
            mentor_village_ids = list(mentor.profile.assigned_villages.values_list('id', flat=True))
            village_ids.extend(mentor_village_ids)

    # Remove duplicates
    village_ids = list(set(village_ids))

    # Get all villages for display
    if village_ids:
        all_villages = Village.objects.filter(id__in=village_ids)

    # Get households in all villages from supervised mentors
    fa_households = Household.objects.filter(village_id__in=village_ids) if village_ids else Household.objects.none()

    # Date ranges - Use current month for accurate monthly counts
    today = timezone.now().date()
    month_start = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)

    # Get trainings by supervised mentors
    mentor_ids = list(supervised_mentors.values_list('id', flat=True))
    fa_trainings = Training.objects.filter(assigned_mentor_id__in=mentor_ids) if mentor_ids else Training.objects.none()

    # Get mentoring activities - Include FA's own visits PLUS supervised mentors' visits
    # Build list of users whose activities to count (FA + supervised mentors)
    activity_users = list(supervised_mentors)
    activity_users.append(user)  # Include FA's own activities

    # Current month visits and calls
    month_visits = MentoringVisit.objects.filter(
        mentor__in=activity_users,
        visit_date__gte=month_start
    ).select_related('mentor', 'household').order_by('-visit_date')

    month_calls = PhoneNudge.objects.filter(
        mentor__in=activity_users,
        call_date__gte=month_start
    ).select_related('mentor', 'household').order_by('-call_date')

    # Also get recent (30 days) for display
    recent_visits = MentoringVisit.objects.filter(
        mentor__in=activity_users,
        visit_date__gte=thirty_days_ago
    ).select_related('mentor', 'household').order_by('-visit_date')

    recent_calls = PhoneNudge.objects.filter(
        mentor__in=activity_users,
        call_date__gte=thirty_days_ago
    ).select_related('mentor', 'household').order_by('-call_date')

    # Calculate total duration for the month
    month_visit_duration = month_visits.aggregate(total=Sum('duration_minutes'))['total'] or 0
    month_call_duration = month_calls.aggregate(total=Sum('duration_minutes'))['total'] or 0
    total_month_duration = month_visit_duration + month_call_duration

    # Field Associate specific metrics
    stats = {
        'managed_mentors': supervised_mentors.count(),
        'total_households': fa_households.count(),
        'total_villages': len(village_ids),
        'total_trainings': fa_trainings.count(),
        'active_trainings': fa_trainings.filter(status='active').count(),
        'households_in_training': HouseholdTrainingEnrollment.objects.filter(
            household__in=fa_households,
            enrollment_status='enrolled'
        ).count() if fa_households.exists() else 0,
        'visits_this_month': month_visits.count(),
        'calls_this_month': month_calls.count(),
        'visit_duration_this_month': month_visit_duration,
        'call_duration_this_month': month_call_duration,
        'total_duration_this_month': total_month_duration,
        'total_hours': total_month_duration // 60,
        'total_minutes': total_month_duration % 60,
    }

    # Mentor performance summary - Use current month for accurate counts
    # Include FA's own performance first
    mentor_performance = []

    # Add FA's own activity first
    fa_month_visits = MentoringVisit.objects.filter(mentor=user, visit_date__gte=month_start)
    fa_month_calls = PhoneNudge.objects.filter(mentor=user, call_date__gte=month_start)
    fa_visits_count = fa_month_visits.count()
    fa_calls_count = fa_month_calls.count()
    fa_visit_duration = fa_month_visits.aggregate(total=Sum('duration_minutes'))['total'] or 0
    fa_call_duration = fa_month_calls.aggregate(total=Sum('duration_minutes'))['total'] or 0

    if fa_visits_count > 0 or fa_calls_count > 0:
        mentor_performance.append({
            'mentor': user,
            'name': (user.get_full_name() or user.username) + ' (You)',
            'households': fa_households.count() if fa_households else 0,
            'villages': len(village_ids),
            'visits_30d': fa_visits_count,
            'calls_30d': fa_calls_count,
            'visit_duration': fa_visit_duration,
            'call_duration': fa_call_duration,
            'total_activity': fa_visits_count + fa_calls_count,
            'total_duration': fa_visit_duration + fa_call_duration,
            'is_fa': True,
        })

    # Add supervised mentors' performance
    for mentor in supervised_mentors:
        mentor_villages = []
        if hasattr(mentor, 'profile') and mentor.profile:
            mentor_villages = list(mentor.profile.assigned_villages.values_list('id', flat=True))

        mentor_households = Household.objects.filter(village_id__in=mentor_villages).count() if mentor_villages else 0

        # Current month visits and calls
        mentor_month_visits = MentoringVisit.objects.filter(
            mentor=mentor,
            visit_date__gte=month_start
        )
        mentor_month_calls = PhoneNudge.objects.filter(
            mentor=mentor,
            call_date__gte=month_start
        )

        mentor_visits_count = mentor_month_visits.count()
        mentor_calls_count = mentor_month_calls.count()
        mentor_visit_duration = mentor_month_visits.aggregate(total=Sum('duration_minutes'))['total'] or 0
        mentor_call_duration = mentor_month_calls.aggregate(total=Sum('duration_minutes'))['total'] or 0

        mentor_performance.append({
            'mentor': mentor,
            'name': mentor.get_full_name() or mentor.username,
            'households': mentor_households,
            'villages': len(mentor_villages),
            'visits_30d': mentor_visits_count,
            'calls_30d': mentor_calls_count,
            'visit_duration': mentor_visit_duration,
            'call_duration': mentor_call_duration,
            'total_activity': mentor_visits_count + mentor_calls_count,
            'total_duration': mentor_visit_duration + mentor_call_duration,
        })

    # Sort by total activity (most active first), but keep FA at top if they have activity
    mentor_performance.sort(key=lambda x: (not x.get('is_fa', False), -x['total_activity']))

    # Enhanced: Alerts for FA (based on villages from their mentors)
    alerts = get_dashboard_alerts(user=user, village_ids=village_ids)

    # Enhanced: Data quality for FA's villages (from mentors)
    data_quality = DataQualityService.get_quality_report(village_ids)

    context = {
        'user': user,
        'stats': stats,
        'supervised_mentors': supervised_mentors,
        'mentor_performance': mentor_performance,
        'all_villages': all_villages,
        'recent_visits': recent_visits[:10],
        'recent_calls': recent_calls[:10],
        'dashboard_type': 'field_associate',
        'alerts': alerts,
        'data_quality': data_quality,
    }

    return render(request, 'dashboard/field_associate_dashboard.html', context)


@login_required
def general_dashboard_view(request):
    """General dashboard for users without specific roles"""
    user = request.user

    # Basic statistics
    stats = {
        'total_households': Household.objects.count(),
        'total_business_groups': BusinessGroup.objects.count(),
        'total_trainings': Training.objects.count(),
        'system_users': user._meta.model.objects.count(),
    }

    context = {
        'user': user,
        'stats': stats,
        'dashboard_type': 'general',
    }

    return render(request, 'dashboard/general_dashboard.html', context)


@login_required
def activity_logs_view(request):
    """
    Activity logs view showing visits and calls with filtering options.
    Accessible to FA, M&E, PM, and Admin.
    Shows monthly records by default with options for 1, 6, or 12 month periods.
    """
    from accounts.models import User
    from django.db.models import Sum
    from calendar import monthrange

    user = request.user

    # Get filter parameters
    period = request.GET.get('period', '1')  # Default to current month (1 month)
    mentor_id = request.GET.get('mentor', '')
    activity_type = request.GET.get('type', 'all')  # 'all', 'visits', 'calls'

    # Calculate date range based on period
    today = timezone.now().date()

    if period == '1':
        # Current month
        start_date = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end_date = today.replace(day=last_day)
        period_label = today.strftime('%B %Y')
    elif period == '6':
        # Last 6 months
        start_date = today - relativedelta(months=6)
        end_date = today
        period_label = f"Last 6 Months ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})"
    elif period == '12':
        # Last 12 months
        start_date = today - relativedelta(months=12)
        end_date = today
        period_label = f"Last 12 Months ({start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')})"
    else:
        # Default to current month
        start_date = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end_date = today.replace(day=last_day)
        period_label = today.strftime('%B %Y')

    # Determine which mentors to show based on role
    mentor_filter = None
    available_mentors = User.objects.none()

    if user.role == 'field_associate':
        # FA sees their supervised mentors
        supervised_mentors = User.objects.filter(
            role='mentor',
            is_active=True,
            profile__supervisor=user
        )
        available_mentors = supervised_mentors
        mentor_filter = supervised_mentors
    elif user.role in ['me_staff', 'program_manager', 'ict_admin']:
        # M&E, PM, and Admin see all mentors
        available_mentors = User.objects.filter(role='mentor', is_active=True)
        mentor_filter = available_mentors
    elif user.role == 'mentor':
        # Mentors see only their own data
        mentor_filter = User.objects.filter(pk=user.pk)
        available_mentors = mentor_filter

    # Filter by specific mentor if selected
    if mentor_id and mentor_filter:
        try:
            mentor_filter = mentor_filter.filter(pk=int(mentor_id))
        except (ValueError, TypeError):
            pass

    # Get visits
    visits = MentoringVisit.objects.filter(
        visit_date__gte=start_date,
        visit_date__lte=end_date
    ).select_related('mentor', 'household').order_by('-visit_date', '-created_at')

    if mentor_filter is not None:
        visits = visits.filter(mentor__in=mentor_filter)

    # Get calls
    calls = PhoneNudge.objects.filter(
        call_date__gte=start_date,
        call_date__lte=end_date
    ).select_related('mentor', 'household').order_by('-call_date', '-created_at')

    if mentor_filter is not None:
        calls = calls.filter(mentor__in=mentor_filter)

    # Calculate totals
    total_visits = visits.count()
    total_calls = calls.count()
    total_visit_duration = visits.aggregate(total=Sum('duration_minutes'))['total'] or 0
    total_call_duration = calls.aggregate(total=Sum('duration_minutes'))['total'] or 0
    total_duration = total_visit_duration + total_call_duration

    # Convert duration to hours and minutes
    total_hours = total_duration // 60
    total_minutes = total_duration % 60

    # Format durations for display
    visit_hours = total_visit_duration // 60
    visit_minutes = total_visit_duration % 60
    call_hours = total_call_duration // 60
    call_minutes = total_call_duration % 60

    # Monthly breakdown for charts
    monthly_data = []
    if period in ['6', '12']:
        months_count = int(period)
        for i in range(months_count):
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            _, last_day = monthrange(month_date.year, month_date.month)
            month_end = month_date.replace(day=last_day)

            month_visits = visits.filter(visit_date__gte=month_start, visit_date__lte=month_end).count()
            month_calls = calls.filter(call_date__gte=month_start, call_date__lte=month_end).count()

            monthly_data.insert(0, {
                'month': month_date.strftime('%b %Y'),
                'visits': month_visits,
                'calls': month_calls,
                'total': month_visits + month_calls
            })

    # Apply type filter for display
    if activity_type == 'visits':
        calls = PhoneNudge.objects.none()
    elif activity_type == 'calls':
        visits = MentoringVisit.objects.none()

    context = {
        'user': user,
        'visits': visits[:100],  # Limit for performance
        'calls': calls[:100],
        'total_visits': total_visits,
        'total_calls': total_calls,
        'total_visit_duration': total_visit_duration,
        'total_call_duration': total_call_duration,
        'total_duration': total_duration,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'visit_hours': visit_hours,
        'visit_minutes': visit_minutes,
        'call_hours': call_hours,
        'call_minutes': call_minutes,
        'period': period,
        'period_label': period_label,
        'start_date': start_date,
        'end_date': end_date,
        'mentor_id': mentor_id,
        'activity_type': activity_type,
        'available_mentors': available_mentors,
        'monthly_data': monthly_data,
        'can_export': user.role in ['me_staff', 'program_manager', 'ict_admin', 'field_associate'],
    }

    return render(request, 'dashboard/activity_logs.html', context)


@login_required
def export_activity_logs(request):
    """
    Export activity logs to CSV
    """
    import csv
    from django.http import HttpResponse
    from accounts.models import User
    from django.db.models import Sum
    from calendar import monthrange

    user = request.user

    # Only allow certain roles to export
    if user.role not in ['me_staff', 'program_manager', 'ict_admin', 'field_associate']:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You don't have permission to export data.")

    # Get filter parameters
    period = request.GET.get('period', '1')
    mentor_id = request.GET.get('mentor', '')
    activity_type = request.GET.get('type', 'all')

    # Calculate date range
    today = timezone.now().date()

    if period == '1':
        start_date = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end_date = today.replace(day=last_day)
    elif period == '6':
        start_date = today - relativedelta(months=6)
        end_date = today
    elif period == '12':
        start_date = today - relativedelta(months=12)
        end_date = today
    else:
        start_date = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end_date = today.replace(day=last_day)

    # Determine mentor filter based on role
    mentor_filter = None

    if user.role == 'field_associate':
        mentor_filter = User.objects.filter(role='mentor', is_active=True, profile__supervisor=user)
    elif user.role in ['me_staff', 'program_manager', 'ict_admin']:
        mentor_filter = User.objects.filter(role='mentor', is_active=True)

    if mentor_id and mentor_filter:
        try:
            mentor_filter = mentor_filter.filter(pk=int(mentor_id))
        except (ValueError, TypeError):
            pass

    # Create response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="activity_logs_{start_date}_{end_date}.csv"'

    writer = csv.writer(response)

    # Get data
    if activity_type in ['all', 'visits']:
        visits = MentoringVisit.objects.filter(
            visit_date__gte=start_date,
            visit_date__lte=end_date
        ).select_related('mentor', 'household').order_by('-visit_date')

        if mentor_filter is not None:
            visits = visits.filter(mentor__in=mentor_filter)

        writer.writerow(['VISITS'])
        writer.writerow(['Date', 'Mentor', 'Household', 'Visit Type', 'Duration (min)', 'Topic', 'Notes'])

        for visit in visits:
            writer.writerow([
                visit.visit_date.strftime('%Y-%m-%d %H:%M'),
                visit.mentor.get_full_name() or visit.mentor.username,
                visit.household.name if visit.household else 'N/A',
                visit.get_visit_type_display(),
                visit.duration_minutes or 0,
                visit.topic or '',
                visit.observations or ''
            ])

        total_visit_duration = visits.aggregate(total=Sum('duration_minutes'))['total'] or 0
        writer.writerow([])
        writer.writerow(['Total Visits:', visits.count(), '', '', f'{total_visit_duration} min'])
        writer.writerow([])

    if activity_type in ['all', 'calls']:
        calls = PhoneNudge.objects.filter(
            call_date__gte=start_date,
            call_date__lte=end_date
        ).select_related('mentor', 'household').order_by('-call_date')

        if mentor_filter is not None:
            calls = calls.filter(mentor__in=mentor_filter)

        writer.writerow(['PHONE CALLS'])
        writer.writerow(['Date', 'Mentor', 'Household', 'Call Type', 'Duration (min)', 'Contact Success', 'Notes'])

        for call in calls:
            writer.writerow([
                call.call_date.strftime('%Y-%m-%d %H:%M'),
                call.mentor.get_full_name() or call.mentor.username,
                call.household.name if call.household else 'N/A',
                call.get_nudge_type_display(),
                call.duration_minutes or 0,
                'Yes' if call.successful_contact else 'No',
                call.notes or ''
            ])

        total_call_duration = calls.aggregate(total=Sum('duration_minutes'))['total'] or 0
        writer.writerow([])
        writer.writerow(['Total Calls:', calls.count(), '', '', f'{total_call_duration} min'])

    return response