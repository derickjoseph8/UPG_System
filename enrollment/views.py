"""
Enrollment views for UPG Kenya MIS
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import EnrollmentApplication, TargetingRule, Verification, ApplicationStatus
from households.models import Household
from core.models import Village, Program
import json


@login_required
def enrollment_dashboard(request):
    """Enrollment dashboard"""
    applications = EnrollmentApplication.objects.all()

    # Statistics
    stats = {
        'total': applications.count(),
        'submitted': applications.filter(status=ApplicationStatus.SUBMITTED).count(),
        'screening': applications.filter(status=ApplicationStatus.SCREENING).count(),
        'approved': applications.filter(status=ApplicationStatus.APPROVED).count(),
        'enrolled': applications.filter(status=ApplicationStatus.ENROLLED).count(),
        'rejected': applications.filter(status=ApplicationStatus.REJECTED).count(),
    }

    # Recent applications
    recent_applications = applications.order_by('-created_at')[:10]

    context = {
        'stats': stats,
        'recent_applications': recent_applications,
    }
    return render(request, 'enrollment/dashboard.html', context)


@login_required
def application_list(request):
    """List all enrollment applications"""
    applications = EnrollmentApplication.objects.select_related(
        'program', 'village', 'submitted_by', 'household'
    ).all()

    # Filtering
    status = request.GET.get('status')
    program_id = request.GET.get('program')
    village_id = request.GET.get('village')
    search = request.GET.get('search')

    if status:
        applications = applications.filter(status=status)
    if program_id:
        applications = applications.filter(program_id=program_id)
    if village_id:
        applications = applications.filter(village_id=village_id)
    if search:
        applications = applications.filter(
            Q(application_id__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(id_number__icontains=search) |
            Q(phone_number__icontains=search)
        )

    applications = applications.order_by('-created_at')

    # Get filter options
    programs = Program.objects.filter(status='active')
    villages = Village.objects.all()

    context = {
        'applications': applications,
        'programs': programs,
        'villages': villages,
        'status_choices': ApplicationStatus.choices,
        'current_status': status,
        'current_program': program_id,
        'current_village': village_id,
        'search_query': search,
    }
    return render(request, 'enrollment/application_list.html', context)


@login_required
def application_detail(request, application_id):
    """View application details"""
    application = get_object_or_404(
        EnrollmentApplication.objects.select_related(
            'program', 'village', 'submitted_by', 'approved_by', 'household'
        ),
        id=application_id
    )

    # Get verifications
    verifications = application.verifications.select_related('verified_by').all()

    context = {
        'application': application,
        'verifications': verifications,
    }
    return render(request, 'enrollment/application_detail.html', context)


@login_required
def application_create(request):
    """Create new enrollment application"""
    if request.method == 'POST':
        try:
            # Create application
            application = EnrollmentApplication.objects.create(
                first_name=request.POST.get('first_name'),
                middle_name=request.POST.get('middle_name', ''),
                last_name=request.POST.get('last_name'),
                id_number=request.POST.get('id_number'),
                phone_number=request.POST.get('phone_number'),
                village_id=request.POST.get('village'),
                program_id=request.POST.get('program'),
                application_data=json.loads(request.POST.get('application_data', '{}')),
                submitted_by=request.user,
                status=ApplicationStatus.SUBMITTED
            )

            messages.success(request, f'Application {application.application_id} created successfully!')
            return redirect('enrollment:application_detail', application_id=application.id)

        except Exception as e:
            messages.error(request, f'Error creating application: {str(e)}')

    # Get form data
    programs = Program.objects.filter(status='active')
    villages = Village.objects.all()

    context = {
        'programs': programs,
        'villages': villages,
    }
    return render(request, 'enrollment/application_create.html', context)


@login_required
def application_screen(request, application_id):
    """Screen application"""
    application = get_object_or_404(EnrollmentApplication, id=application_id)

    if request.method == 'POST':
        screening_score = float(request.POST.get('screening_score', 0))
        screening_passed = request.POST.get('screening_passed') == 'true'
        screening_notes = request.POST.get('screening_notes', '')

        application.screening_score = screening_score
        application.screening_passed = screening_passed
        application.screening_date = timezone.now()
        application.screening_notes = screening_notes

        if screening_passed:
            application.status = ApplicationStatus.ID_VALIDATION
            application.current_step = 'id_validation'
        else:
            application.status = ApplicationStatus.REJECTED
            application.rejection_reason = 'Failed screening criteria'

        application.save()

        messages.success(request, 'Application screening completed!')
        return redirect('enrollment:application_detail', application_id=application.id)

    # Get targeting rules for program
    targeting_rules = []
    if application.program:
        targeting_rules = TargetingRule.objects.filter(
            program=application.program,
            is_active=True
        ).order_by('priority')

    context = {
        'application': application,
        'targeting_rules': targeting_rules,
    }
    return render(request, 'enrollment/application_screen.html', context)


@login_required
def application_approve(request, application_id):
    """Approve or reject application"""
    application = get_object_or_404(EnrollmentApplication, id=application_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            application.approved = True
            application.approved_by = request.user
            application.approved_date = timezone.now()
            application.status = ApplicationStatus.APPROVED
            messages.success(request, 'Application approved!')

        elif action == 'reject':
            application.approved = False
            application.rejection_reason = request.POST.get('rejection_reason', '')
            application.status = ApplicationStatus.REJECTED
            messages.success(request, 'Application rejected!')

        application.save()
        return redirect('enrollment:application_detail', application_id=application.id)

    context = {
        'application': application,
    }
    return render(request, 'enrollment:application_approve.html', context)


@login_required
def validate_id_number(request):
    """AJAX endpoint to validate ID number"""
    id_number = request.GET.get('id_number')

    if not id_number:
        return JsonResponse({'valid': False, 'message': 'ID number is required'})

    # Check if ID number already exists in applications
    existing_app = EnrollmentApplication.objects.filter(id_number=id_number).first()
    if existing_app:
        return JsonResponse({
            'valid': False,
            'message': f'ID number already exists in application {existing_app.application_id}'
        })

    # Check if ID number exists in households
    existing_household = Household.objects.filter(id_number=id_number).first()
    if existing_household:
        return JsonResponse({
            'valid': False,
            'message': f'ID number already exists for household {existing_household.name}'
        })

    # Basic validation (Kenya ID format: 8 digits or birth cert format)
    if len(id_number) < 6:
        return JsonResponse({'valid': False, 'message': 'ID number must be at least 6 characters'})

    return JsonResponse({'valid': True, 'message': 'ID number is valid'})


@login_required
def validate_phone_number(request):
    """AJAX endpoint to validate phone number"""
    phone_number = request.GET.get('phone_number')

    if not phone_number:
        return JsonResponse({'valid': False, 'message': 'Phone number is required'})

    # Basic Kenya phone number validation
    # Kenya phone numbers: +254... or 07... or 01...
    import re
    phone_pattern = r'^(\+254|0)[17]\d{8}$'

    if not re.match(phone_pattern, phone_number):
        return JsonResponse({
            'valid': False,
            'message': 'Invalid Kenya phone number format. Use +254XXXXXXXXX or 07XXXXXXXX'
        })

    return JsonResponse({'valid': True, 'message': 'Phone number is valid'})
