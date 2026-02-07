from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from .models import (
    Program, ProgramApplication, ProgramBeneficiary,
    ProgramFieldAssociate, ProgramMentorAssignment, ProgramNotification
)
from households.models import Household
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def program_list(request):
    """List all programs - filtered by role"""
    user = request.user
    user_role = getattr(user, 'role', None)

    # Base queryset
    base_programs = Program.objects.filter(status__in=['active', 'draft'])

    # Filter by role
    if user.is_superuser or user_role in ['ict_admin', 'me_staff', 'program_manager', 'county_executive']:
        # Full access to all programs
        programs = base_programs
        my_programs = None
    elif user_role == 'field_associate':
        # FAs see programs they're assigned to
        my_program_ids = ProgramFieldAssociate.objects.filter(
            field_associate=user
        ).values_list('program_id', flat=True)
        programs = base_programs.filter(id__in=my_program_ids)
        my_programs = programs
    elif user_role == 'mentor':
        # Mentors see programs they're assigned to via their FA
        my_program_ids = ProgramMentorAssignment.objects.filter(
            mentor=user
        ).values_list('program_fa__program_id', flat=True)
        programs = base_programs.filter(id__in=my_program_ids)
        my_programs = programs
    else:
        # Other roles see all active programs (for applying)
        programs = base_programs.filter(status='active')
        my_programs = None

    programs = programs.order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        programs = programs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(county__icontains=search_query)
        )

    # Filter by program type
    program_type = request.GET.get('type')
    if program_type:
        programs = programs.filter(program_type=program_type)

    # Pagination
    paginator = Paginator(programs, 10)
    page_number = request.GET.get('page')
    programs = paginator.get_page(page_number)

    context = {
        'programs': programs,
        'program_types': Program.PROGRAM_TYPE_CHOICES,
        'search_query': search_query,
        'selected_type': program_type,
        'page_title': 'My Programs' if user_role in ['mentor', 'field_associate'] else 'Programs',
        'user_role': user_role,
    }

    return render(request, 'programs/program_list.html', context)

@login_required
def program_create(request):
    """Create a new program (County Executives, ICT Admins, Program Managers, and Superusers)"""
    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['county_executive', 'ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to create programs.')
        return redirect('programs:program_list')

    # Get all Field Associates for selection
    field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')

    if request.method == 'POST':
        # Basic form processing
        name = request.POST.get('name')
        description = request.POST.get('description')
        program_type = request.POST.get('program_type')
        budget = request.POST.get('budget') or None
        target_beneficiaries = request.POST.get('target_beneficiaries') or 0

        if name and description:
            program = Program.objects.create(
                name=name,
                description=description,
                program_type=program_type,
                budget=budget,
                target_beneficiaries=target_beneficiaries,
                created_by=request.user,
                county=request.POST.get('county', getattr(request.user, 'county', '')),
                eligibility_criteria=request.POST.get('eligibility_criteria', ''),
                application_requirements=request.POST.get('application_requirements', ''),
            )

            # Handle FA assignments
            selected_fas = request.POST.getlist('field_associates[]') or request.POST.getlist('field_associates')
            select_all_fas = request.POST.get('select_all_fas') == 'on'

            if select_all_fas:
                # Add all FAs
                fas_to_add = field_associates
            else:
                # Add selected FAs
                fas_to_add = User.objects.filter(id__in=selected_fas, role='field_associate')

            for fa in fas_to_add:
                # Create FA assignment
                pfa = ProgramFieldAssociate.objects.create(
                    program=program,
                    field_associate=fa,
                    assigned_by=request.user,
                    status='pending'
                )

                # Create notification for FA
                ProgramNotification.objects.create(
                    recipient=fa,
                    program=program,
                    notification_type='fa_assignment',
                    title=f'New Program Assignment: {program.name}',
                    message=f'You have been assigned to the program "{program.name}" by {request.user.get_full_name()}. Please assign mentors to this program.',
                    action_url=reverse('programs:assign_mentors', kwargs={'pk': program.pk})
                )

                # Mark as notified
                pfa.notified = True
                pfa.notified_at = timezone.now()
                pfa.save()

            fa_count = fas_to_add.count() if hasattr(fas_to_add, 'count') else len(list(fas_to_add))
            if fa_count > 0:
                messages.success(request, f'Program "{program.name}" created and {fa_count} Field Associate(s) have been notified to assign mentors!')
            else:
                messages.success(request, f'Program "{program.name}" created successfully!')

            return redirect('programs:program_detail', pk=program.pk)
        else:
            messages.error(request, 'Name and description are required.')

    context = {
        'program_types': Program.PROGRAM_TYPE_CHOICES,
        'field_associates': field_associates,
        'page_title': 'Create New Program',
    }

    return render(request, 'programs/program_create.html', context)

@login_required
def program_detail(request, pk):
    """Program detail view"""
    program = get_object_or_404(Program, pk=pk)
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check if current user has already applied
    user_application = None
    if hasattr(user, 'household'):
        try:
            user_application = ProgramApplication.objects.get(
                program=program,
                household=user.household
            )
        except ProgramApplication.DoesNotExist:
            pass

    # Check user's role in this program
    is_assigned_fa = False
    is_assigned_mentor = False
    mentor_assignment = None
    fa_assignment = None

    if user_role == 'field_associate':
        fa_assignment = ProgramFieldAssociate.objects.filter(
            program=program, field_associate=user
        ).first()
        if fa_assignment:
            is_assigned_fa = True
    elif user_role == 'mentor':
        mentor_assignment = ProgramMentorAssignment.objects.select_related('program_fa').filter(
            program_fa__program=program, mentor=user
        ).first()
        if mentor_assignment:
            is_assigned_mentor = True

    # Check if user can manage this program
    can_manage = (
        user.is_superuser or
        user_role in ['ict_admin', 'program_manager'] or
        user == program.created_by or
        is_assigned_fa or
        is_assigned_mentor
    )

    context = {
        'program': program,
        'user_application': user_application,
        'can_apply': program.is_accepting_applications and not user_application,
        'page_title': program.name,
        'user_role': user_role,
        'is_assigned_fa': is_assigned_fa,
        'is_assigned_mentor': is_assigned_mentor,
        'mentor_assignment': mentor_assignment,
        'fa_assignment': fa_assignment,
        'can_manage': can_manage,
    }

    return render(request, 'programs/program_detail.html', context)

@login_required
def program_applications(request, pk):
    """View applications for a program (Program creators, admins, and superusers)"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or
            request.user == program.created_by or
            user_role in ['ict_admin', 'me_staff']):
        messages.error(request, 'You do not have permission to view applications.')
        return redirect('programs:program_detail', pk=program.pk)

    applications = program.applications.all().order_by('-application_date')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'program': program,
        'applications': applications,
        'status_choices': ProgramApplication.APPLICATION_STATUS_CHOICES,
        'selected_status': status_filter,
        'page_title': f'{program.name} - Applications',
    }

    return render(request, 'programs/program_applications.html', context)

@login_required
def program_apply(request, pk):
    """Apply to a program"""
    program = get_object_or_404(Program, pk=pk)

    if not program.is_accepting_applications:
        messages.error(request, 'This program is not accepting applications.')
        return redirect('programs:program_detail', pk=program.pk)

    # Get or create household for user
    try:
        household = request.user.household
    except:
        messages.error(request, 'You need to be associated with a household to apply.')
        return redirect('programs:program_detail', pk=program.pk)

    # Check if already applied
    if ProgramApplication.objects.filter(program=program, household=household).exists():
        messages.warning(request, 'You have already applied to this program.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        motivation_letter = request.POST.get('motivation_letter', '')
        additional_notes = request.POST.get('additional_notes', '')

        application = ProgramApplication.objects.create(
            program=program,
            household=household,
            motivation_letter=motivation_letter,
            additional_notes=additional_notes,
        )

        messages.success(request, 'Your application has been submitted successfully!')
        return redirect('programs:program_detail', pk=program.pk)

    context = {
        'program': program,
        'page_title': f'Apply to {program.name}',
    }

    return render(request, 'programs/program_apply.html', context)

@login_required
def my_applications(request):
    """View user's applications"""
    applications = []

    try:
        household = request.user.household
        applications = ProgramApplication.objects.filter(household=household).order_by('-application_date')
    except:
        pass

    context = {
        'applications': applications,
        'page_title': 'My Applications',
    }

    return render(request, 'programs/my_applications.html', context)

@login_required
def program_delete(request, pk):
    """Delete program (Superusers and ICT Admins only)"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role == 'ict_admin'):
        messages.error(request, 'You do not have permission to delete programs.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        program_name = program.name
        program.delete()
        messages.success(request, f'Program "{program_name}" has been deleted successfully!')
        return redirect('programs:program_list')

    # Count related objects that will be affected
    applications_count = program.applications.count()
    business_groups_count = getattr(program, 'businessgroup_set', None)
    if business_groups_count:
        business_groups_count = business_groups_count.count()
    else:
        business_groups_count = 0

    context = {
        'program': program,
        'applications_count': applications_count,
        'business_groups_count': business_groups_count,
        'page_title': f'Delete Program - {program.name}',
    }
    return render(request, 'programs/program_delete.html', context)

@login_required
def program_edit(request, pk):
    """Edit program (County Executives, ICT Admins, Superusers, and program creators)"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or
            request.user == program.created_by or
            user_role in ['ict_admin', 'county_executive']):
        messages.error(request, 'You do not have permission to edit this program.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        # Update program fields
        program.name = request.POST.get('name', program.name)
        program.description = request.POST.get('description', program.description)
        program.program_type = request.POST.get('program_type', program.program_type)
        program.budget = request.POST.get('budget') or program.budget
        program.target_beneficiaries = request.POST.get('target_beneficiaries') or program.target_beneficiaries
        program.eligibility_criteria = request.POST.get('eligibility_criteria', program.eligibility_criteria)
        program.application_requirements = request.POST.get('application_requirements', program.application_requirements)

        program.save()
        messages.success(request, f'Program "{program.name}" updated successfully!')
        return redirect('programs:program_detail', pk=program.pk)

    context = {
        'program': program,
        'program_types': Program.PROGRAM_TYPE_CHOICES,
        'page_title': f'Edit {program.name}',
    }

    return render(request, 'programs/program_edit.html', context)

@login_required
def program_toggle_status(request, pk):
    """Toggle program status between active/paused/ended"""
    program = get_object_or_404(Program, pk=pk)

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or
            request.user == program.created_by or
            user_role in ['ict_admin', 'county_executive']):
        messages.error(request, 'You do not have permission to change program status.')
        return redirect('programs:program_detail', pk=program.pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['active', 'paused', 'ended', 'draft']:
            old_status = program.get_status_display()
            program.status = new_status
            program.save()
            messages.success(request, f'Program status changed from {old_status} to {program.get_status_display()}')
        else:
            messages.error(request, 'Invalid status provided.')

    return redirect('programs:program_detail', pk=program.pk)


@login_required
def approve_application(request, application_id):
    """Approve a program application"""
    from django.utils import timezone

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['county_executive', 'ict_admin', 'me_staff']):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    application = get_object_or_404(ProgramApplication, id=application_id)

    if request.method == 'POST':
        try:
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()

            # Create program beneficiary entry
            ProgramBeneficiary.objects.get_or_create(
                program=application.program,
                household=application.household,
                defaults={
                    'enrollment_date': timezone.now().date(),
                    'status': 'active'
                }
            )

            return JsonResponse({
                'success': True,
                'message': f'Application for {application.household.name} has been approved'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def reject_application(request, application_id):
    """Reject a program application"""

    user_role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or user_role in ['county_executive', 'ict_admin', 'me_staff']):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    application = get_object_or_404(ProgramApplication, id=application_id)

    if request.method == 'POST':
        try:
            application.status = 'rejected'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.rejection_reason = request.POST.get('reason', '')
            application.save()

            return JsonResponse({
                'success': True,
                'message': f'Application for {application.household.name} has been rejected'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def assign_mentors(request, pk):
    """FA view to assign mentors to a program"""
    program = get_object_or_404(Program, pk=pk)
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check if user is an FA assigned to this program or has admin privileges
    is_admin = user.is_superuser or user_role in ['ict_admin', 'program_manager']
    fa_assignment = None

    if user_role == 'field_associate':
        try:
            fa_assignment = ProgramFieldAssociate.objects.get(program=program, field_associate=user)
        except ProgramFieldAssociate.DoesNotExist:
            if not is_admin:
                messages.error(request, 'You are not assigned to this program.')
                return redirect('programs:program_list')

    if not fa_assignment and not is_admin:
        messages.error(request, 'You do not have permission to assign mentors to this program.')
        return redirect('programs:program_list')

    # Get available mentors (mentors supervised by this FA)
    available_mentors = []
    if fa_assignment:
        # Get mentors supervised by this FA
        if hasattr(user, 'profile') and user.profile:
            available_mentors = list(user.profile.supervised_mentors.filter(is_active=True))
    elif is_admin:
        # Admins can see all mentors
        available_mentors = list(User.objects.filter(role='mentor', is_active=True))

    # Get already assigned mentors for this FA
    assigned_mentor_ids = []
    if fa_assignment:
        assigned_mentor_ids = list(fa_assignment.mentor_assignments.values_list('mentor_id', flat=True))

    if request.method == 'POST':
        # Handle mentor assignment
        selected_mentors = request.POST.getlist('mentors[]') or request.POST.getlist('mentors')
        select_all = request.POST.get('select_all_mentors') == 'on'

        if select_all:
            mentors_to_add = available_mentors
        else:
            mentors_to_add = User.objects.filter(id__in=selected_mentors, role='mentor')

        added_count = 0
        for mentor in mentors_to_add:
            # Check if already assigned
            if fa_assignment:
                if not ProgramMentorAssignment.objects.filter(program_fa=fa_assignment, mentor=mentor).exists():
                    ProgramMentorAssignment.objects.create(
                        program_fa=fa_assignment,
                        mentor=mentor,
                        assigned_by=user
                    )
                    added_count += 1

        # Update FA assignment status
        if fa_assignment and added_count > 0:
            fa_assignment.status = 'assigned'
            fa_assignment.save()

        if added_count > 0:
            messages.success(request, f'{added_count} mentor(s) assigned to program successfully!')

            # Notify PM that mentors have been assigned
            if program.created_by:
                ProgramNotification.objects.create(
                    recipient=program.created_by,
                    program=program,
                    notification_type='program_update',
                    title=f'Mentors Assigned to {program.name}',
                    message=f'{user.get_full_name()} has assigned {added_count} mentor(s) to the program "{program.name}".',
                    action_url=reverse('programs:program_detail', kwargs={'pk': program.pk})
                )
        else:
            messages.info(request, 'No new mentors were assigned.')

        return redirect('programs:assign_mentors', pk=program.pk)

    # Get all FA assignments for this program (for admin view)
    all_fa_assignments = program.field_associates.all().select_related('field_associate')

    context = {
        'program': program,
        'fa_assignment': fa_assignment,
        'available_mentors': available_mentors,
        'assigned_mentor_ids': assigned_mentor_ids,
        'all_fa_assignments': all_fa_assignments,
        'is_admin': is_admin,
        'page_title': f'Assign Mentors - {program.name}',
    }

    return render(request, 'programs/assign_mentors.html', context)


@login_required
def remove_mentor_assignment(request, assignment_id):
    """Remove a mentor assignment from a program"""
    assignment = get_object_or_404(ProgramMentorAssignment, id=assignment_id)
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions
    is_admin = user.is_superuser or user_role in ['ict_admin', 'program_manager']
    is_fa_owner = assignment.program_fa.field_associate == user

    if not (is_admin or is_fa_owner):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            mentor_name = assignment.mentor.get_full_name()
            program_name = assignment.program_fa.program.name
            assignment.delete()

            return JsonResponse({
                'success': True,
                'message': f'{mentor_name} removed from {program_name}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def my_notifications(request):
    """View user's program notifications"""
    notifications = ProgramNotification.objects.filter(recipient=request.user).order_by('-created_at')

    # Mark as read if viewing
    if request.GET.get('mark_read') == 'all':
        notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        messages.success(request, 'All notifications marked as read.')
        return redirect('programs:my_notifications')

    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications[:50],  # Limit to 50
        'unread_count': unread_count,
        'page_title': 'My Notifications',
    }

    return render(request, 'programs/my_notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(ProgramNotification, id=notification_id, recipient=request.user)

    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()

    if notification.action_url:
        return redirect(notification.action_url)

    return redirect('programs:my_notifications')


@login_required
def program_team(request, pk):
    """View program team (FAs and Mentors)"""
    program = get_object_or_404(Program, pk=pk)
    user_role = getattr(request.user, 'role', None)

    # Check permissions
    if not (request.user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff'] or
            request.user == program.created_by):
        messages.error(request, 'You do not have permission to view the program team.')
        return redirect('programs:program_detail', pk=pk)

    fa_assignments = program.field_associates.all().select_related('field_associate', 'assigned_by')

    # Get mentor counts for each FA
    for fa in fa_assignments:
        fa.mentors = fa.mentor_assignments.select_related('mentor').all()

    context = {
        'program': program,
        'fa_assignments': fa_assignments,
        'page_title': f'Program Team - {program.name}',
    }

    return render(request, 'programs/program_team.html', context)


@login_required
def add_fa_to_program(request, pk):
    """Add Field Associates to an existing program"""
    program = get_object_or_404(Program, pk=pk)
    user_role = getattr(request.user, 'role', None)

    # Check permissions
    if not (request.user.is_superuser or user_role in ['ict_admin', 'program_manager'] or
            request.user == program.created_by):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        selected_fas = request.POST.getlist('field_associates[]') or request.POST.getlist('field_associates')
        select_all = request.POST.get('select_all_fas') == 'on'

        if select_all:
            fas_to_add = User.objects.filter(role='field_associate', is_active=True)
        else:
            fas_to_add = User.objects.filter(id__in=selected_fas, role='field_associate')

        # Exclude already assigned FAs
        existing_fa_ids = program.field_associates.values_list('field_associate_id', flat=True)
        fas_to_add = fas_to_add.exclude(id__in=existing_fa_ids)

        added_count = 0
        for fa in fas_to_add:
            pfa = ProgramFieldAssociate.objects.create(
                program=program,
                field_associate=fa,
                assigned_by=request.user,
                status='pending'
            )

            # Create notification
            ProgramNotification.objects.create(
                recipient=fa,
                program=program,
                notification_type='fa_assignment',
                title=f'New Program Assignment: {program.name}',
                message=f'You have been assigned to the program "{program.name}" by {request.user.get_full_name()}. Please assign mentors to this program.',
                action_url=reverse('programs:assign_mentors', kwargs={'pk': program.pk})
            )

            pfa.notified = True
            pfa.notified_at = timezone.now()
            pfa.save()
            added_count += 1

        if added_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'{added_count} Field Associate(s) added and notified!'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'No new Field Associates to add.'
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def get_unread_notification_count(request):
    """API to get unread notification count"""
    count = ProgramNotification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def enroll_households(request, pk):
    """Enroll households into a program - for mentors and FAs"""
    program = get_object_or_404(Program, pk=pk)
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions - must be assigned to this program or be admin
    is_admin = user.is_superuser or user_role in ['ict_admin', 'program_manager']
    is_assigned_fa = ProgramFieldAssociate.objects.filter(program=program, field_associate=user).exists()
    is_assigned_mentor = ProgramMentorAssignment.objects.filter(program_fa__program=program, mentor=user).exists()

    if not (is_admin or is_assigned_fa or is_assigned_mentor):
        messages.error(request, 'You do not have permission to enroll households in this program.')
        return redirect('programs:program_detail', pk=pk)

    # Get households based on role - mentors see households from their assigned villages
    from households.models import Household

    if user_role == 'mentor' and not is_admin:
        # Mentors see all households in villages they are assigned to
        if hasattr(user, 'profile') and user.profile:
            assigned_village_ids = user.profile.assigned_villages.values_list('id', flat=True)
            available_households = Household.objects.filter(village_id__in=assigned_village_ids)
        else:
            available_households = Household.objects.none()
    elif user_role == 'field_associate' and not is_admin:
        # FAs see all households in villages assigned to their supervised mentors
        if hasattr(user, 'profile') and user.profile:
            # Get all villages assigned to mentors supervised by this FA
            supervised_mentors = user.profile.supervised_mentors.all()
            village_ids = set()
            for mentor_user in supervised_mentors:
                if hasattr(mentor_user, 'profile') and mentor_user.profile:
                    mentor_villages = mentor_user.profile.assigned_villages.values_list('id', flat=True)
                    village_ids.update(mentor_villages)
            available_households = Household.objects.filter(village_id__in=village_ids)
        else:
            available_households = Household.objects.none()
    else:
        # Admins see all households
        available_households = Household.objects.all()

    # Exclude already enrolled households in this specific program
    enrolled_household_ids = ProgramBeneficiary.objects.filter(program=program).values_list('household_id', flat=True)
    available_households = available_households.exclude(id__in=enrolled_household_ids).select_related('village')

    if request.method == 'POST':
        selected_households = request.POST.getlist('households[]') or request.POST.getlist('households')
        select_all = request.POST.get('select_all_households') == 'on'

        if select_all:
            households_to_add = available_households
        else:
            households_to_add = available_households.filter(id__in=selected_households)

        added_count = 0
        for household in households_to_add:
            # Check if already enrolled
            if not ProgramBeneficiary.objects.filter(program=program, household=household).exists():
                ProgramBeneficiary.objects.create(
                    program=program,
                    household=household,
                    enrollment_date=timezone.now().date(),
                    participation_status='active'
                )
                added_count += 1

        if added_count > 0:
            messages.success(request, f'{added_count} household(s) enrolled in the program successfully!')
        else:
            messages.info(request, 'No new households were enrolled.')

        return redirect('programs:program_beneficiaries', pk=pk)

    context = {
        'program': program,
        'available_households': available_households,
        'page_title': f'Enroll Households - {program.name}',
        'user_role': user_role,
    }

    return render(request, 'programs/enroll_households.html', context)


@login_required
def program_beneficiaries(request, pk):
    """View program beneficiaries"""
    program = get_object_or_404(Program, pk=pk)
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions
    is_admin = user.is_superuser or user_role in ['ict_admin', 'program_manager', 'me_staff']
    is_assigned_fa = ProgramFieldAssociate.objects.filter(program=program, field_associate=user).exists()
    is_assigned_mentor = ProgramMentorAssignment.objects.filter(program_fa__program=program, mentor=user).exists()
    is_creator = user == program.created_by

    if not (is_admin or is_assigned_fa or is_assigned_mentor or is_creator):
        messages.error(request, 'You do not have permission to view beneficiaries.')
        return redirect('programs:program_detail', pk=pk)

    # Get beneficiaries
    beneficiaries = program.beneficiaries.select_related('household__village').order_by('-enrollment_date')

    # Filter for mentors - only show households from their assigned villages
    if user_role == 'mentor' and not is_admin:
        if hasattr(user, 'profile') and user.profile:
            assigned_village_ids = user.profile.assigned_villages.values_list('id', flat=True)
            beneficiaries = beneficiaries.filter(household__village_id__in=assigned_village_ids)
        else:
            beneficiaries = beneficiaries.none()
    elif user_role == 'field_associate' and not is_admin:
        # FAs see households from villages assigned to their supervised mentors
        if hasattr(user, 'profile') and user.profile:
            supervised_mentors = user.profile.supervised_mentors.all()
            village_ids = set()
            for mentor_user in supervised_mentors:
                if hasattr(mentor_user, 'profile') and mentor_user.profile:
                    mentor_villages = mentor_user.profile.assigned_villages.values_list('id', flat=True)
                    village_ids.update(mentor_villages)
            beneficiaries = beneficiaries.filter(household__village_id__in=village_ids)

    # Statistics
    total_beneficiaries = beneficiaries.count()
    active_beneficiaries = beneficiaries.filter(participation_status='active').count()
    graduated_beneficiaries = beneficiaries.filter(participation_status='graduated').count()

    context = {
        'program': program,
        'beneficiaries': beneficiaries,
        'total_beneficiaries': total_beneficiaries,
        'active_beneficiaries': active_beneficiaries,
        'graduated_beneficiaries': graduated_beneficiaries,
        'page_title': f'Beneficiaries - {program.name}',
        'user_role': user_role,
        'can_enroll': is_admin or is_assigned_fa or is_assigned_mentor,
    }

    return render(request, 'programs/program_beneficiaries.html', context)


@login_required
def remove_beneficiary(request, beneficiary_id):
    """Remove a beneficiary from a program"""
    beneficiary = get_object_or_404(ProgramBeneficiary, id=beneficiary_id)
    user = request.user
    user_role = getattr(user, 'role', None)

    # Check permissions
    is_admin = user.is_superuser or user_role in ['ict_admin', 'program_manager']

    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        try:
            household_name = beneficiary.household.name
            program_name = beneficiary.program.name
            beneficiary.delete()

            return JsonResponse({
                'success': True,
                'message': f'{household_name} removed from {program_name}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
