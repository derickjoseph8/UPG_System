from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Training, TrainingAttendance, TrainingFieldAssociate, TrainingMentorAssignment
from households.models import Household

@login_required
def training_list(request):
    """Training Sessions list view with role-based filtering"""
    from core.models import BusinessMentorCycle, Mentor
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = request.user
    user_role = getattr(user, 'role', None)

    # Filter trainings based on user role and assignments
    if user.is_superuser or user_role in ['ict_admin', 'me_staff', 'program_manager']:
        # Full access to all trainings
        training_sessions = Training.objects.all()
    elif user_role == 'field_associate':
        # FAs see trainings assigned to them via TrainingFieldAssociate
        my_training_ids = TrainingFieldAssociate.objects.filter(
            field_associate=user
        ).values_list('training_id', flat=True)
        training_sessions = Training.objects.filter(id__in=my_training_ids)
    elif user_role == 'mentor':
        # Mentors see trainings assigned to them via TrainingMentorAssignment
        my_training_ids = TrainingMentorAssignment.objects.filter(
            mentor=user
        ).values_list('training_fa__training_id', flat=True)
        # Also include trainings where they're directly assigned (legacy)
        legacy_training_ids = Training.objects.filter(assigned_mentor=user).values_list('id', flat=True)
        all_training_ids = set(my_training_ids) | set(legacy_training_ids)
        training_sessions = Training.objects.filter(id__in=all_training_ids)
    else:
        # Other roles have no access to trainings
        training_sessions = Training.objects.none()

    training_sessions = training_sessions.order_by('-created_at')

    # Add stats for each training
    from django.db.models import Count, Q
    training_sessions = training_sessions.annotate(
        enrolled_count=Count('attendances__household', distinct=True),
        present_count=Count('attendances', filter=Q(attendances__attendance=True)),
        total_attendance_records=Count('attendances')
    )

    # Calculate stats summary
    planned_count = training_sessions.filter(status='planned').count()
    active_count = training_sessions.filter(status='active').count()
    completed_count = training_sessions.filter(status='completed').count()

    # Get BM Cycles based on role
    if user_role == 'mentor':
        # Mentors see only BM cycles they are attached to
        if hasattr(user, 'mentor_profile'):
            bm_cycles = BusinessMentorCycle.objects.filter(business_mentor=user.mentor_profile)
        else:
            bm_cycles = BusinessMentorCycle.objects.none()
    elif user_role == 'field_associate':
        # FAs see BM cycles for their supervised mentors
        supervised_mentor_ids = []
        if hasattr(user, 'profile') and user.profile:
            supervised_users = user.profile.supervised_mentors
            for su in supervised_users:
                if hasattr(su, 'mentor_profile'):
                    supervised_mentor_ids.append(su.mentor_profile.id)
        bm_cycles = BusinessMentorCycle.objects.filter(business_mentor_id__in=supervised_mentor_ids)
    elif user_role == 'program_manager':
        # PMs see all BM cycles
        bm_cycles = BusinessMentorCycle.objects.all()
    else:
        # Admins see all
        bm_cycles = BusinessMentorCycle.objects.all()

    # Get Mentors for assignment dropdown based on role
    current_mentor_user = None
    available_mentors = []

    if user_role == 'mentor':
        # Mentors auto-select themselves
        current_mentor_user = user
        available_mentors = [user]  # Only show themselves
    elif user_role == 'field_associate':
        # FAs see their supervised mentors
        if hasattr(user, 'profile') and user.profile:
            available_mentors = list(user.profile.supervised_mentors)
    elif user_role == 'program_manager':
        # PMs see all mentors
        available_mentors = list(User.objects.filter(role='mentor', is_active=True))
    else:
        # Admins see all mentors
        available_mentors = list(User.objects.filter(role='mentor', is_active=True))

    # Get available Field Associates for assignment (for PM/Admin roles)
    field_associates = []
    can_assign_fa = user.is_superuser or user_role in ['ict_admin', 'me_staff', 'program_manager']
    if can_assign_fa:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')

    context = {
        'training_sessions': training_sessions,
        'page_title': 'Training Sessions',
        'total_count': training_sessions.count(),
        'planned_count': planned_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'bm_cycles': bm_cycles,
        'available_mentors': available_mentors,
        'current_mentor_user': current_mentor_user,
        'user_role': user_role,
        'field_associates': field_associates,
        'can_assign_fa': can_assign_fa,
    }

    return render(request, 'training/training_list.html', context)

@login_required
def training_details(request, training_id):
    """Training details page"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return HttpResponseForbidden()

    # Get related data
    attendances = training.attendances.select_related('household__village', 'marked_by').order_by('household__name')

    # Calculate training statistics
    total_enrolled = attendances.count()
    present_count = attendances.filter(attendance=True).count()
    absent_count = total_enrolled - present_count
    attendance_rate = round((present_count * 100) / total_enrolled) if total_enrolled > 0 else 0
    enrollment_rate = round((total_enrolled * 100) / training.max_households) if training.max_households > 0 else 0

    # Get recent activity (last 10 attendance changes)
    recent_activity = attendances.filter(attendance_marked_at__isnull=False).order_by('-attendance_marked_at')[:10]

    context = {
        'training': training,
        'attendances': attendances,
        'page_title': f'Training Details - {training.name}',
        'total_enrolled': total_enrolled,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': attendance_rate,
        'enrollment_rate': enrollment_rate,
        'recent_activity': recent_activity,
    }

    return render(request, 'training/training_details.html', context)

@login_required
@require_http_methods(["POST"])
def start_training(request, training_id):
    """AJAX endpoint to start a training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if training.status != 'planned':
        return JsonResponse({'success': False, 'message': 'Training can only be started if it is in planned status'})

    training.status = 'active'
    if not training.start_date:
        training.start_date = timezone.now().date()
    training.save()

    return JsonResponse({'success': True, 'message': 'Training started successfully'})

@login_required
@require_http_methods(["POST"])
def complete_training(request, training_id):
    """AJAX endpoint to complete a training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if training.status != 'active':
        return JsonResponse({'success': False, 'message': 'Training can only be completed if it is active'})

    training.status = 'completed'
    if not training.end_date:
        training.end_date = timezone.now().date()
    training.save()

    return JsonResponse({'success': True, 'message': 'Training completed successfully'})

@login_required
@require_http_methods(["DELETE"])
def delete_training(request, training_id):
    """AJAX endpoint to delete a training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions - only admin roles can delete
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff']):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    # Check if training has attendances
    if training.attendances.exists():
        return JsonResponse({'success': False, 'message': 'Cannot delete training with existing attendance records'})

    training_name = training.name
    training.delete()

    return JsonResponse({'success': True, 'message': f'Training "{training_name}" deleted successfully'})

@login_required
def manage_attendance(request, training_id):
    """Training attendance management interface with daily attendance support"""
    from datetime import datetime, timedelta

    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'program_manager'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return HttpResponseForbidden()

    # Get selected date from request or use today's date
    # Support both 'date' parameter (from dropdown) and 'custom_date' (from date input)
    selected_date_str = request.GET.get('date') or request.GET.get('custom_date')
    if selected_date_str and selected_date_str != 'custom':
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    # Get training dates - if training_dates is set, use it; otherwise use start_date
    training_dates = []
    if training.training_dates and isinstance(training.training_dates, list):
        training_dates = [datetime.strptime(d, '%Y-%m-%d').date() if isinstance(d, str) else d for d in training.training_dates]
    elif training.start_date:
        # Generate dates from start to end (or just start date if no end date)
        if training.end_date:
            current_date = training.start_date
            while current_date <= training.end_date:
                training_dates.append(current_date)
                current_date += timedelta(days=1)
        else:
            training_dates = [training.start_date]

    # If no dates configured, use current date
    if not training_dates:
        training_dates = [timezone.now().date()]

    # Add dates that have attendance records (for historical retroactive entries)
    attendance_dates = training.attendances.values_list('training_date', flat=True).distinct()
    for att_date in attendance_dates:
        if att_date and att_date not in training_dates:
            training_dates.append(att_date)

    # If selected date not in training dates, add it (allows any date to be selected)
    if selected_date not in training_dates:
        training_dates.append(selected_date)

    # Sort dates
    training_dates.sort()

    # Filter attendances for the selected date
    attendances = training.attendances.filter(training_date=selected_date).select_related('household__village', 'marked_by').order_by('household__name')

    # Get unique households enrolled (from all dates)
    enrolled_households = training.attendances.values_list('household', flat=True).distinct()
    total_unique_enrolled = len(set(enrolled_households))

    # Calculate attendance statistics for selected date
    total_enrolled = attendances.count()
    present_count = attendances.filter(attendance=True).count()
    absent_count = total_enrolled - present_count
    attendance_rate = round((present_count * 100) / total_enrolled) if total_enrolled > 0 else 0

    context = {
        'training': training,
        'attendances': attendances,
        'page_title': f'Manage Attendance - {training.name}',
        'total_enrolled': total_enrolled,
        'total_unique_enrolled': total_unique_enrolled,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_rate': attendance_rate,
        'selected_date': selected_date,
        'training_dates': sorted(training_dates),
    }

    return render(request, 'training/manage_attendance.html', context)

@login_required
@require_http_methods(["POST"])
def create_training(request):
    """Create a new training session"""
    from django.shortcuts import redirect
    from django.contrib import messages

    user = request.user

    # Check permissions - mentors, FA, and PM can create/schedule trainings
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'mentor', 'program_manager']):
        messages.error(request, 'Permission denied')
        return redirect('training:training_list')

    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        # Extract form data
        name = request.POST.get('name', '').strip()
        module_id = request.POST.get('module_id', '').strip()
        bm_cycle_id = request.POST.get('bm_cycle')
        assigned_mentor_id = request.POST.get('assigned_mentor')
        start_date = request.POST.get('start_date')
        max_households = request.POST.get('max_households', 25)
        time_taken = request.POST.get('time_taken')
        status = request.POST.get('status', 'planned')
        description = request.POST.get('description', '').strip()

        # Validation
        errors = {}
        if not name:
            errors['name'] = ['Training name is required']
        if not module_id:
            errors['module_id'] = ['Module ID is required']

        # Validate BM Cycle exists if provided
        bm_cycle = None
        if bm_cycle_id:
            try:
                from core.models import BusinessMentorCycle
                bm_cycle = BusinessMentorCycle.objects.get(id=bm_cycle_id)
            except BusinessMentorCycle.DoesNotExist:
                errors['bm_cycle'] = ['Invalid BM Cycle selected']

        # Validate mentor exists if provided
        assigned_mentor = None
        if assigned_mentor_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                assigned_mentor = User.objects.get(id=assigned_mentor_id, role='mentor')
            except User.DoesNotExist:
                errors['assigned_mentor'] = ['Invalid mentor selected']

        # Validate max households
        try:
            max_households = int(max_households)
            if max_households < 1 or max_households > 50:
                errors['max_households'] = ['Max households must be between 1 and 50']
        except (ValueError, TypeError):
            errors['max_households'] = ['Invalid number for max households']

        # Validate duration if provided
        time_taken_obj = None
        if time_taken:
            try:
                from datetime import timedelta
                # Expected format: "HH:MM:SS"
                parts = time_taken.split(':')
                hours = int(parts[0])
                minutes = int(parts[1]) if len(parts) > 1 else 0
                seconds = int(parts[2]) if len(parts) > 2 else 0
                time_taken_obj = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except (ValueError, IndexError):
                errors['time_taken'] = ['Invalid duration format']

        # Validate start date if provided
        start_date_obj = None
        if start_date:
            try:
                from datetime import datetime
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                errors['start_date'] = ['Invalid date format']

        if errors:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors})
            else:
                for field, error_list in errors.items():
                    for error in error_list:
                        messages.error(request, f'{field}: {error}')
                return redirect('training:training_list')

        # Create training
        training = Training.objects.create(
            name=name,
            module_id=module_id,
            bm_cycle=bm_cycle,
            assigned_mentor=assigned_mentor,
            time_taken=time_taken_obj,
            description=description,
            status=status,
            start_date=start_date_obj,
            max_households=max_households
        )

        # Handle Field Associate assignments (for PM/Admin roles)
        fa_ids = request.POST.getlist('field_associates[]') or request.POST.getlist('field_associates')
        if fa_ids and (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'program_manager']):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            for fa_id in fa_ids:
                try:
                    fa_user = User.objects.get(id=fa_id, role='field_associate')
                    TrainingFieldAssociate.objects.create(
                        training=training,
                        field_associate=fa_user,
                        assigned_by=user,
                        status='pending'
                    )
                except User.DoesNotExist:
                    pass

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Training "{training.name}" created successfully',
                'training_id': training.id
            })
        else:
            messages.success(request, f'Training "{training.name}" created successfully!')
            return redirect('training:training_list')

    except Exception as e:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': f'Error creating training: {str(e)}'
            })
        else:
            messages.error(request, f'Error creating training: {str(e)}')
            return redirect('training:training_list')


@login_required
def edit_training(request, training_id):
    """Edit an existing training session"""
    training = get_object_or_404(Training, id=training_id)
    user = request.user

    # Check permissions - mentors can edit trainings they're assigned to
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    if request.method == 'GET':
        # Return training data for the edit form
        from core.models import BusinessMentorCycle, Mentor
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get available options for form
        bm_cycles = BusinessMentorCycle.objects.all()
        mentors = User.objects.filter(role='mentor')

        # Calculate training statistics
        total_enrolled = training.attendances.count()
        present_count = training.attendances.filter(attendance=True).count()
        completion_rate = round((total_enrolled * 100) / training.max_households) if training.max_households > 0 else 0

        context = {
            'training': training,
            'bm_cycles': bm_cycles,
            'mentors': mentors,
            'page_title': f'Edit Training - {training.name}',
            'present_count': present_count,
            'completion_rate': completion_rate,
        }
        return render(request, 'training/edit_training.html', context)

    elif request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name', '').strip()
            module_id = request.POST.get('module_id', '').strip()
            bm_cycle_id = request.POST.get('bm_cycle')
            assigned_mentor_id = request.POST.get('assigned_mentor')
            start_date = request.POST.get('start_date')
            max_households = request.POST.get('max_households', 25)
            time_taken = request.POST.get('time_taken')
            status = request.POST.get('status', training.status)
            description = request.POST.get('description', '').strip()
            module_number = request.POST.get('module_number')
            duration_hours = request.POST.get('duration_hours')
            location = request.POST.get('location', '').strip()
            participant_count = request.POST.get('participant_count')

            # Validation
            errors = {}
            if not name:
                errors['name'] = ['Training name is required']
            if not module_id:
                errors['module_id'] = ['Module ID is required']

            # Validate BM Cycle exists if provided
            bm_cycle = None
            if bm_cycle_id:
                try:
                    from core.models import BusinessMentorCycle
                    bm_cycle = BusinessMentorCycle.objects.get(id=bm_cycle_id)
                except BusinessMentorCycle.DoesNotExist:
                    errors['bm_cycle'] = ['Invalid BM Cycle selected']

            # Validate mentor exists if provided
            assigned_mentor = None
            if assigned_mentor_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    assigned_mentor = User.objects.get(id=assigned_mentor_id, role='mentor')
                except User.DoesNotExist:
                    errors['assigned_mentor'] = ['Invalid mentor selected']

            # Validate max households
            try:
                max_households = int(max_households)
                if max_households < 1 or max_households > 50:
                    errors['max_households'] = ['Max households must be between 1 and 50']
            except (ValueError, TypeError):
                errors['max_households'] = ['Invalid number for max households']

            # Validate duration if provided
            time_taken_obj = None
            if time_taken:
                try:
                    from datetime import timedelta
                    # Expected format: "HH:MM:SS"
                    parts = time_taken.split(':')
                    hours = int(parts[0])
                    minutes = int(parts[1]) if len(parts) > 1 else 0
                    seconds = int(parts[2]) if len(parts) > 2 else 0
                    time_taken_obj = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except (ValueError, IndexError):
                    errors['time_taken'] = ['Invalid duration format']

            # Validate start date if provided
            start_date_obj = None
            if start_date:
                try:
                    from datetime import datetime
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    errors['start_date'] = ['Invalid date format']

            # Validate module number if provided
            module_number_obj = None
            if module_number:
                try:
                    module_number_obj = int(module_number)
                except ValueError:
                    errors['module_number'] = ['Module number must be a valid integer']

            # Validate duration hours if provided
            duration_hours_obj = None
            if duration_hours:
                try:
                    duration_hours_obj = float(duration_hours)
                except ValueError:
                    errors['duration_hours'] = ['Duration hours must be a valid number']

            # Validate participant count if provided
            participant_count_obj = None
            if participant_count:
                try:
                    participant_count_obj = int(participant_count)
                except ValueError:
                    errors['participant_count'] = ['Participant count must be a valid integer']

            if errors:
                return JsonResponse({'success': False, 'errors': errors})

            # Update training
            training.name = name
            training.module_id = module_id
            training.bm_cycle = bm_cycle
            training.assigned_mentor = assigned_mentor
            training.time_taken = time_taken_obj
            training.description = description
            training.status = status
            training.start_date = start_date_obj
            training.max_households = max_households
            training.module_number = module_number_obj
            training.duration_hours = duration_hours_obj
            training.location = location
            training.participant_count = participant_count_obj
            training.save()

            return JsonResponse({
                'success': True,
                'message': f'Training "{training.name}" updated successfully',
                'training_id': training.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating training: {str(e)}'
            })


@login_required
def get_available_households(request, training_id):
    """Get list of households available to add to training"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    # Get households that are not already in this training
    enrolled_household_ids = training.attendances.values_list('household_id', flat=True)
    available_households = Household.objects.exclude(id__in=enrolled_household_ids).select_related('village')

    households_data = []
    for household in available_households:
        households_data.append({
            'id': household.id,
            'name': household.name,
            'village': household.village.name,
            'phone': household.phone_number
        })

    return JsonResponse({
        'success': True,
        'households': households_data
    })


@login_required
@require_http_methods(["POST"])
def add_household_to_training(request, training_id):
    """Add one or multiple households to training attendance (bulk add supported)"""
    training = get_object_or_404(Training, id=training_id)

    # Check permissions
    user = request.user
    if not (user.is_superuser or user.role in ['ict_admin', 'me_staff', 'field_associate', 'program_manager'] or
            (user.role == 'mentor' and training.assigned_mentor == user)):
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    try:
        # Support both single household_id and multiple household_ids[]
        household_ids = request.POST.getlist('household_ids[]') or request.POST.getlist('household_ids')
        single_household_id = request.POST.get('household_id')

        # If single ID provided, convert to list
        if single_household_id and not household_ids:
            household_ids = [single_household_id]

        training_date = request.POST.get('training_date')

        if not household_ids:
            return JsonResponse({'success': False, 'message': 'At least one household is required'})

        if not training_date:
            return JsonResponse({'success': False, 'message': 'Training date is required'})

        # Parse training date
        from datetime import datetime, timedelta
        from households.models import Household
        training_date_obj = datetime.strptime(training_date, '%Y-%m-%d').date()

        # Check training capacity
        current_count = training.attendances.values('household').distinct().count()
        available_slots = training.max_households - current_count if training.max_households else 999

        if len(household_ids) > available_slots:
            return JsonResponse({
                'success': False,
                'message': f'Only {available_slots} slot(s) available. You selected {len(household_ids)} households.'
            })

        added_count = 0
        skipped_count = 0
        added_names = []

        for hh_id in household_ids:
            try:
                household = Household.objects.get(id=hh_id)

                # Check if household is already in this training
                if training.attendances.filter(household=household).exists():
                    skipped_count += 1
                    continue

                # Create attendance record
                TrainingAttendance.objects.create(
                    training=training,
                    household=household,
                    training_date=training_date_obj,
                    attendance=True,
                    marked_by=user,
                    attendance_marked_at=timezone.now()
                )
                added_count += 1
                added_names.append(household.name)

                # Mark absent for previous dates if applicable
                if training.start_date and training_date_obj > training.start_date:
                    current_date = training.start_date
                    while current_date < training_date_obj:
                        if not training.end_date or current_date <= training.end_date:
                            if not training.attendances.filter(household=household, training_date=current_date).exists():
                                TrainingAttendance.objects.create(
                                    training=training,
                                    household=household,
                                    training_date=current_date,
                                    attendance=False,
                                    marked_by=user,
                                    attendance_marked_at=timezone.now()
                                )
                        current_date += timedelta(days=1)

            except Household.DoesNotExist:
                skipped_count += 1
                continue

        if added_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'No households were added. They may already be enrolled.'
            })

        message = f'Successfully added {added_count} household(s) to training'
        if skipped_count > 0:
            message += f' ({skipped_count} skipped - already enrolled)'

        return JsonResponse({
            'success': True,
            'message': message,
            'added_count': added_count,
            'skipped_count': skipped_count,
            'added_names': added_names[:5]  # Return first 5 names
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding household: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def toggle_attendance(request, attendance_id):
    """Toggle attendance status for a household"""
    attendance = get_object_or_404(TrainingAttendance, id=attendance_id)

    # Check permissions
    user = request.user
    user_role = getattr(user, 'role', None)

    # Allow: superuser, admin roles, FA, PM, or any mentor
    # Mentors can mark attendance - they can only see their assigned trainings anyway
    has_permission = (
        user.is_superuser or
        user_role in ['ict_admin', 'me_staff', 'field_associate', 'program_manager', 'mentor']
    )

    if not has_permission:
        return JsonResponse({'success': False, 'message': 'Permission denied.'})

    try:
        new_attendance = request.POST.get('attendance') == 'true'
        attendance.attendance = new_attendance
        attendance.marked_by = user
        attendance.attendance_marked_at = timezone.now()
        attendance.save()

        return JsonResponse({
            'success': True,
            'message': f'Attendance updated for {attendance.household.name}',
            'attendance': new_attendance
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating attendance: {str(e)}'
        })


@login_required
@require_http_methods(["DELETE"])
def remove_attendance(request, attendance_id):
    """Remove a household from training attendance"""
    attendance = get_object_or_404(TrainingAttendance, id=attendance_id)

    # Check permissions
    user = request.user
    user_role = getattr(user, 'role', None)

    # Allow: superuser, admin roles, FA, PM, or any mentor
    has_permission = (
        user.is_superuser or
        user_role in ['ict_admin', 'me_staff', 'field_associate', 'program_manager', 'mentor']
    )

    if not has_permission:
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    try:
        household_name = attendance.household.name
        attendance.delete()

        return JsonResponse({
            'success': True,
            'message': f'Household "{household_name}" removed from training'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error removing household: {str(e)}'
        })


@login_required
def training_assign_mentors(request, training_id):
    """FA assigns mentors to a training they're assigned to"""
    from django.contrib.auth import get_user_model
    from django.contrib import messages
    User = get_user_model()

    user = request.user
    training = get_object_or_404(Training, id=training_id)

    # Check if user is FA assigned to this training
    try:
        fa_assignment = TrainingFieldAssociate.objects.get(
            training=training,
            field_associate=user
        )
    except TrainingFieldAssociate.DoesNotExist:
        # Allow admin roles to also manage mentor assignments
        if not (user.is_superuser or user.role in ['me_staff', 'ict_admin', 'program_manager']):
            messages.error(request, 'You are not assigned to manage this training')
            return redirect('training:training_list')
        fa_assignment = None

    if request.method == 'POST':
        mentor_ids = request.POST.getlist('mentors[]') or request.POST.getlist('mentors')

        if fa_assignment:
            # Get current mentor assignments for this FA
            current_mentor_ids = set(TrainingMentorAssignment.objects.filter(
                training_fa=fa_assignment
            ).values_list('mentor_id', flat=True))

            new_mentor_ids = set(int(m_id) for m_id in mentor_ids if m_id)

            # Add new mentor assignments
            added_count = 0
            for mentor_id in new_mentor_ids - current_mentor_ids:
                try:
                    mentor = User.objects.get(id=mentor_id, role='mentor')
                    TrainingMentorAssignment.objects.create(
                        training_fa=fa_assignment,
                        mentor=mentor,
                        assigned_by=user
                    )
                    added_count += 1
                except User.DoesNotExist:
                    pass

            # Remove mentor assignments that are no longer selected
            removed_count = TrainingMentorAssignment.objects.filter(
                training_fa=fa_assignment,
                mentor_id__in=(current_mentor_ids - new_mentor_ids)
            ).delete()[0]

            messages.success(request, f'Mentor assignments updated. Added: {added_count}, Removed: {removed_count}')
        else:
            messages.info(request, 'Admin mentor assignment not yet implemented for non-FA users')

        return redirect('training:training_assign_mentors', training_id=training_id)

    # GET request - show assignment page
    # Get available mentors (FA's supervised mentors)
    if user.role == 'field_associate' and hasattr(user, 'profile') and user.profile:
        available_mentors = list(user.profile.supervised_mentors)
    else:
        # Admin roles see all mentors
        available_mentors = list(User.objects.filter(role='mentor', is_active=True))

    # Get currently assigned mentors
    assigned_mentor_ids = []
    if fa_assignment:
        assigned_mentor_ids = list(TrainingMentorAssignment.objects.filter(
            training_fa=fa_assignment
        ).values_list('mentor_id', flat=True))

    context = {
        'page_title': f'Assign Mentors - {training.name}',
        'training': training,
        'fa_assignment': fa_assignment,
        'available_mentors': available_mentors,
        'assigned_mentor_ids': assigned_mentor_ids,
    }

    return render(request, 'training/training_assign_mentors.html', context)


@login_required
def training_fa_assignments_list(request):
    """List all trainings assigned to the current FA with their mentor assignments"""
    from django.contrib import messages

    user = request.user

    if user.role != 'field_associate':
        messages.error(request, 'This page is for Field Associates only')
        return redirect('training:training_list')

    # Get trainings assigned to this FA
    fa_assignments = TrainingFieldAssociate.objects.filter(
        field_associate=user
    ).select_related('training', 'assigned_by').order_by('-assigned_at')

    context = {
        'page_title': 'My Training Assignments',
        'fa_assignments': fa_assignments,
    }

    return render(request, 'training/fa_assignments_list.html', context)