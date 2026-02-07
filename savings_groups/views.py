from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date
from decimal import Decimal, InvalidOperation
import csv
import logging
from .models import BusinessSavingsGroup, BSGMember, SavingsRecord, BSGLoan, LoanRepayment
from core.models import Village
from business_groups.models import BusinessGroup
from households.models import Household

logger = logging.getLogger(__name__)


def can_edit_savings(user):
    """Check if user has permission to edit savings entries"""
    # Only PM, ICT Admin, and superusers can edit savings entries
    return user.is_superuser or user.role in ['program_manager', 'ict_admin']


def get_user_accessible_villages(user):
    """
    Get villages accessible by user based on role hierarchy:
    - Mentor: Their assigned villages
    - FA: Villages from their supervised mentors
    - PM/Admin: All villages
    """
    if user.is_superuser or user.role in ['ict_admin', 'program_manager', 'me_staff']:
        return Village.objects.all()

    if user.role == 'field_associate':
        # FA sees villages from supervised mentors
        from accounts.models import User as UserModel
        supervised_mentors = UserModel.objects.filter(
            role='mentor',
            is_active=True,
            profile__supervisor=user
        )
        village_ids = []
        for mentor in supervised_mentors:
            if hasattr(mentor, 'profile') and mentor.profile:
                mentor_villages = list(mentor.profile.assigned_villages.values_list('id', flat=True))
                village_ids.extend(mentor_villages)
        return Village.objects.filter(id__in=list(set(village_ids)))

    if user.role == 'mentor':
        # Mentor sees only their assigned villages
        if hasattr(user, 'profile') and user.profile:
            return user.profile.assigned_villages.all()

    return Village.objects.none()

@login_required
def savings_list(request):
    """Savings Groups list view with role-based filtering and search"""
    user = request.user

    # Search functionality
    search_query = request.GET.get('search', '').strip()

    # Only mentors and field associates have filtered view
    # Everyone else sees all groups
    if user.role in ['mentor', 'field_associate'] and not user.is_superuser:
        # Get accessible villages based on role
        accessible_villages = get_user_accessible_villages(user)

        if accessible_villages.exists():
            # Show groups with members from accessible villages OR created by this user
            savings_groups = BusinessSavingsGroup.objects.filter(
                Q(is_active=True, bsg_members__household__village__in=accessible_villages) |
                Q(created_by=user)
            ).distinct()
        else:
            # No villages accessible - show groups created by this user only
            savings_groups = BusinessSavingsGroup.objects.filter(
                Q(created_by=user)
            ).distinct()
    else:
        # All other roles (ICT Admin, PM, M&E, Executive, etc.) see all groups
        savings_groups = BusinessSavingsGroup.objects.filter(is_active=True)

    # Apply search filter
    if search_query:
        savings_groups = savings_groups.filter(name__icontains=search_query)

    savings_groups = savings_groups.order_by('-formation_date')

    # Calculate totals for the statistics cards
    total_savings = savings_groups.aggregate(total=Sum('savings_to_date'))['total'] or 0
    total_members = BSGMember.objects.filter(
        bsg__in=savings_groups,
        is_active=True
    ).count()

    # Calculate active loans statistics
    active_loans = BSGLoan.objects.filter(
        bsg__in=savings_groups,
        status__in=['active', 'partially_repaid']
    )
    active_loans_count = active_loans.count()
    total_loans_amount = active_loans.aggregate(total=Sum('loan_amount'))['total'] or 0

    context = {
        'savings_groups': savings_groups,
        'page_title': 'Savings Groups',
        'total_count': savings_groups.count(),
        'total_savings': total_savings,
        'total_members': total_members,
        'active_loans_count': active_loans_count,
        'total_loans_amount': total_loans_amount,
        'search_query': search_query,
    }

    return render(request, 'savings_groups/savings_list.html', context)

@login_required
def savings_group_create(request):
    """Create savings group with role-based filtering"""
    user = request.user

    if request.method == 'POST':
        name = request.POST.get('name')
        village_id = request.POST.get('village')
        business_group_id = request.POST.get('business_group')
        target_members = request.POST.get('target_members', 20)

        logger.info(f"SAVINGS CREATE: User {user.username}, Name: {name}, Village: {village_id}, BG: {business_group_id}")

        # Validate village access for mentors
        if user.role in ['mentor', 'field_associate'] and village_id:
            if hasattr(user, 'profile') and user.profile:
                assigned_villages = user.profile.assigned_villages.values_list('id', flat=True)
                if int(village_id) not in assigned_villages:
                    messages.error(request, 'You can only create savings groups in your assigned villages.')
                    village_id = None

        if name:
            formation_date = request.POST.get('formation_date') or date.today()
            meeting_day = request.POST.get('meeting_day', '')
            meeting_location = request.POST.get('meeting_location', '')

            try:
                target_members_int = int(target_members) if target_members else 20
            except ValueError:
                target_members_int = 20

            savings_group = BusinessSavingsGroup.objects.create(
                name=name,
                formation_date=formation_date,
                meeting_day=meeting_day,
                meeting_location=meeting_location,
                members_count=0,
                target_members=target_members_int,
                created_by=user
            )
            logger.info(f"SAVINGS CREATE: Created savings group {savings_group.id} - {savings_group.name}")

            # Associate business group and auto-add its members
            members_added = 0
            if business_group_id:
                try:
                    business_group = BusinessGroup.objects.get(id=business_group_id)
                    savings_group.business_groups.add(business_group)
                    logger.info(f"SAVINGS CREATE: Associated business group {business_group.name}")

                    # Automatically add all business group members to savings group
                    for bg_member in business_group.members.all():
                        # Check if household is not already a member
                        if not BSGMember.objects.filter(bsg=savings_group, household=bg_member.household, is_active=True).exists():
                            BSGMember.objects.create(
                                bsg=savings_group,
                                household=bg_member.household,
                                role='member',
                                joined_date=date.today(),
                                is_active=True
                            )
                            members_added += 1
                    logger.info(f"SAVINGS CREATE: Added {members_added} members from business group")
                except BusinessGroup.DoesNotExist:
                    logger.warning(f"SAVINGS CREATE: Business group {business_group_id} not found")

            if members_added > 0:
                messages.success(request, f'Savings group "{savings_group.name}" created successfully with {members_added} member(s) from business group!')
            else:
                messages.success(request, f'Savings group "{savings_group.name}" created successfully!')
            return redirect('savings_groups:savings_group_detail', pk=savings_group.pk)
        else:
            messages.error(request, 'Savings group name is required.')

    # Filter villages and business groups based on user role
    if user.is_superuser or user.role in ['ict_admin', 'me_staff']:
        villages = Village.objects.all()
        business_groups = BusinessGroup.objects.all()
    elif user.role in ['mentor', 'field_associate']:
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            villages = assigned_villages
            # Business groups with members from assigned villages
            business_groups = BusinessGroup.objects.filter(
                members__household__village__in=assigned_villages
            ).distinct()
        else:
            villages = Village.objects.none()
            business_groups = BusinessGroup.objects.none()
            messages.warning(request, 'You have no assigned villages. Please contact your administrator.')
    else:
        villages = Village.objects.none()
        business_groups = BusinessGroup.objects.none()
        messages.error(request, 'You do not have permission to create savings groups.')

    context = {
        'villages': villages,
        'business_groups': business_groups,
        'page_title': 'Create Savings Group',
    }
    return render(request, 'savings_groups/savings_group_create.html', context)

@login_required
def savings_group_detail(request, pk):
    """Savings group detail view"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    # Get active and inactive members separately
    active_members = savings_group.bsg_members.filter(is_active=True)
    inactive_members = savings_group.bsg_members.filter(is_active=False)

    # Calculate membership percentage
    current_members = active_members.count()
    target_members = savings_group.target_members or 25  # Default target if not set
    membership_percentage = round((current_members * 100) / target_members) if target_members > 0 else 0

    context = {
        'savings_group': savings_group,
        'page_title': f'Savings Group - {savings_group.name}',
        'active_members': active_members,
        'inactive_members': inactive_members,
        'current_members': current_members,
        'membership_percentage': membership_percentage,
    }
    return render(request, 'savings_groups/savings_group_detail.html', context)

@login_required
def savings_group_edit(request, pk):
    """Edit savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        savings_group.name = request.POST.get('name', savings_group.name)
        formation_date = request.POST.get('formation_date')
        if formation_date:
            savings_group.formation_date = formation_date
        savings_group.meeting_day = request.POST.get('meeting_day', savings_group.meeting_day)
        savings_group.meeting_location = request.POST.get('meeting_location', savings_group.meeting_location)

        # Handle savings_frequency
        savings_frequency = request.POST.get('savings_frequency')
        if savings_frequency:
            savings_group.savings_frequency = savings_frequency

        # Handle target_members
        target_members = request.POST.get('target_members')
        if target_members:
            try:
                savings_group.target_members = int(target_members)
            except ValueError:
                pass  # Keep existing value if invalid input

        savings_group.save()
        messages.success(request, f'Savings group "{savings_group.name}" updated successfully!')
        return redirect('savings_groups:savings_group_detail', pk=savings_group.pk)

    villages = Village.objects.all()
    business_groups = BusinessGroup.objects.all()

    # Calculate membership percentage
    current_members = savings_group.bsg_members.filter(is_active=True).count()
    target_members = savings_group.target_members or 25  # Default target if not set
    membership_percentage = round((current_members * 100) / target_members) if target_members > 0 else 0

    context = {
        'savings_group': savings_group,
        'villages': villages,
        'business_groups': business_groups,
        'page_title': f'Edit - {savings_group.name}',
        'current_members': current_members,
        'membership_percentage': membership_percentage,
    }
    return render(request, 'savings_groups/savings_group_edit.html', context)

@login_required
def add_member(request, pk):
    """Add individual member to savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        household_id = request.POST.get('household')
        role = request.POST.get('role', 'member')
        joined_date = request.POST.get('joined_date') or date.today()

        if household_id:
            try:
                household = Household.objects.get(id=household_id)

                # Check if already a member
                if BSGMember.objects.filter(bsg=savings_group, household=household, is_active=True).exists():
                    messages.warning(request, f'{household.name} is already a member of this savings group.')
                else:
                    BSGMember.objects.create(
                        bsg=savings_group,
                        household=household,
                        role=role,
                        joined_date=joined_date,
                        is_active=True
                    )
                    messages.success(request, f'{household.name} added to {savings_group.name} successfully!')
            except Household.DoesNotExist:
                messages.error(request, 'Selected household does not exist.')
        else:
            messages.error(request, 'Please select a household.')

        return redirect('savings_groups:savings_group_detail', pk=pk)

    # Get available households (not already members)
    existing_member_households = savings_group.bsg_members.filter(is_active=True).values_list('household_id', flat=True)
    available_households = Household.objects.exclude(id__in=existing_member_households)

    # Filter by user's assigned villages for mentors/field associates
    user = request.user
    if user.role in ['mentor', 'field_associate'] and not user.is_superuser:
        if hasattr(user, 'profile') and user.profile:
            assigned_villages = user.profile.assigned_villages.all()
            if assigned_villages.exists():
                available_households = available_households.filter(village__in=assigned_villages)

    available_households = available_households.order_by('head_first_name', 'head_last_name')

    context = {
        'savings_group': savings_group,
        'households': available_households,
        'role_choices': BSGMember.ROLE_CHOICES,
        'page_title': f'Add Member to {savings_group.name}',
    }
    return render(request, 'savings_groups/add_member.html', context)

@login_required
def remove_member(request, pk, member_id):
    """Remove individual member from savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    member = get_object_or_404(BSGMember, id=member_id, bsg=savings_group)

    if request.method == 'POST':
        member.is_active = False
        member.save()
        messages.success(request, f'{member.household.name} removed from {savings_group.name}.')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    context = {
        'savings_group': savings_group,
        'member': member,
        'page_title': f'Remove Member from {savings_group.name}',
    }
    return render(request, 'savings_groups/remove_member_confirm.html', context)

@login_required
def add_business_group(request, pk):
    """Associate business group with savings group and auto-add all members"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        business_group_id = request.POST.get('business_group')

        if business_group_id:
            try:
                business_group = BusinessGroup.objects.get(id=business_group_id)

                # Check if already associated
                if business_group in savings_group.business_groups.all():
                    messages.warning(request, f'{business_group.name} is already part of this savings group.')
                else:
                    # Add business group to savings group
                    savings_group.business_groups.add(business_group)

                    # Automatically add all business group members to savings group
                    members_added = 0
                    for bg_member in business_group.members.all():
                        # Check if household is not already a member
                        if not BSGMember.objects.filter(bsg=savings_group, household=bg_member.household, is_active=True).exists():
                            BSGMember.objects.create(
                                bsg=savings_group,
                                household=bg_member.household,
                                role='member',
                                joined_date=date.today(),
                                is_active=True
                            )
                            members_added += 1

                    messages.success(request, f'{business_group.name} added to {savings_group.name} successfully! {members_added} member(s) added.')
            except BusinessGroup.DoesNotExist:
                messages.error(request, 'Selected business group does not exist.')
        else:
            messages.error(request, 'Please select a business group.')

        return redirect('savings_groups:savings_group_detail', pk=pk)

    # Get available business groups (not already associated)
    available_business_groups = BusinessGroup.objects.exclude(
        id__in=savings_group.business_groups.values_list('id', flat=True)
    ).order_by('name')

    context = {
        'savings_group': savings_group,
        'business_groups': available_business_groups,
        'page_title': f'Add Business Group to {savings_group.name}',
    }
    return render(request, 'savings_groups/add_business_group.html', context)

@login_required
def remove_business_group(request, pk, bg_id):
    """Remove business group from savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    business_group = get_object_or_404(BusinessGroup, id=bg_id)

    if request.method == 'POST':
        savings_group.business_groups.remove(business_group)
        messages.success(request, f'{business_group.name} removed from {savings_group.name}.')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    context = {
        'savings_group': savings_group,
        'business_group': business_group,
        'page_title': f'Remove Business Group from {savings_group.name}',
    }
    return render(request, 'savings_groups/remove_business_group_confirm.html', context)

@login_required
def record_savings(request, pk):
    """Record savings for a savings group meeting"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        savings_date = request.POST.get('savings_date') or date.today()
        notes = request.POST.get('notes', '')
        records_created = 0
        errors = []
        MAX_AMOUNT = Decimal('99999999.99')  # Maximum allowed by DecimalField(max_digits=10, decimal_places=2)

        # Process each member's savings
        for member in savings_group.bsg_members.filter(is_active=True):
            amount_key = f'amount_{member.id}'
            amount_str = request.POST.get(amount_key, '0')

            try:
                # Clean the input - remove commas and extra whitespace
                amount_str = str(amount_str).replace(',', '').strip()
                if not amount_str:
                    continue

                amount = Decimal(amount_str)

                # Validate amount range
                if amount < 0:
                    errors.append(f'{member.household}: Amount cannot be negative')
                    continue
                if amount > MAX_AMOUNT:
                    errors.append(f'{member.household}: Amount too large (max: {MAX_AMOUNT:,.2f})')
                    continue

                if amount > 0:
                    # Create savings record
                    SavingsRecord.objects.create(
                        bsg=savings_group,
                        member=member,
                        amount=amount,
                        savings_date=savings_date,
                        recorded_by=request.user,
                        notes=notes
                    )

                    # Update member's total savings - refresh from DB first to avoid stale data
                    member.refresh_from_db()
                    current_total = member.total_savings or Decimal('0')
                    member.total_savings = current_total + amount
                    member.save()

                    records_created += 1
            except (ValueError, TypeError, InvalidOperation) as e:
                errors.append(f'{member.household}: Invalid amount format')
            except Exception as e:
                logger.error(f"Error recording savings for {member.household}: {str(e)}")
                errors.append(f'{member.household}: Error saving record')

        # Update group's total savings - refresh first
        savings_group.refresh_from_db()
        total_savings = savings_group.bsg_members.filter(is_active=True).aggregate(
            total=Sum('total_savings'))['total'] or Decimal('0')
        savings_group.savings_to_date = total_savings
        savings_group.save()

        if records_created > 0:
            messages.success(request, f'{records_created} savings record(s) created successfully!')
        if errors:
            for error in errors[:5]:  # Show max 5 errors
                messages.error(request, error)
            if len(errors) > 5:
                messages.error(request, f'...and {len(errors) - 5} more errors')
        if records_created == 0 and not errors:
            messages.warning(request, 'No savings amounts were entered.')

        return redirect('savings_groups:savings_group_detail', pk=pk)

    context = {
        'savings_group': savings_group,
        'members': savings_group.bsg_members.filter(is_active=True).order_by('household__name'),
        'page_title': f'Record Savings - {savings_group.name}',
    }
    return render(request, 'savings_groups/record_savings.html', context)


@login_required
def savings_report(request, pk):
    """Generate savings report for a savings group"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Get all savings records
    savings_records = SavingsRecord.objects.filter(bsg=savings_group)

    if date_from:
        savings_records = savings_records.filter(savings_date__gte=date_from)
    if date_to:
        savings_records = savings_records.filter(savings_date__lte=date_to)

    # Calculate totals
    total_savings = savings_records.aggregate(total=Sum('amount'))['total'] or 0

    # Member summaries
    member_summaries = []
    for member in savings_group.bsg_members.filter(is_active=True):
        member_records = savings_records.filter(member=member)
        member_total = member_records.aggregate(total=Sum('amount'))['total'] or 0
        member_summaries.append({
            'member': member,
            'total_savings': member_total,
            'record_count': member_records.count(),
            'latest_savings': member_records.order_by('-savings_date').first(),
        })

    context = {
        'savings_group': savings_group,
        'savings_records': savings_records.order_by('-savings_date'),
        'total_savings': total_savings,
        'member_summaries': member_summaries,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': f'Savings Report - {savings_group.name}',
    }
    return render(request, 'savings_groups/savings_report.html', context)


@login_required
def export_savings_data(request, pk):
    """Export savings data to CSV"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="savings_{savings_group.name}_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Member Name', 'Amount (KES)', 'Recorded By', 'Notes'
    ])

    # Get savings records
    for record in SavingsRecord.objects.filter(bsg=savings_group).order_by('-savings_date'):
        writer.writerow([
            record.savings_date.strftime('%Y-%m-%d'),
            record.member.household.name,
            f"{record.amount:,.2f}",
            record.recorded_by.get_full_name() if record.recorded_by else 'N/A',
            record.notes
        ])

    # Add summary rows
    writer.writerow([])
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Savings:', f"KES {savings_group.savings_to_date:,.2f}"])
    writer.writerow(['Total Members:', savings_group.bsg_members.filter(is_active=True).count()])
    writer.writerow(['Savings Frequency:', savings_group.get_savings_frequency_display()])

    return response


@login_required
def edit_savings_record(request, pk, record_id):
    """Edit a savings record - ONLY PM and ICT Admin can edit"""
    user = request.user

    # Permission check - only PM and ICT Admin can edit savings records
    if not can_edit_savings(user):
        messages.error(request, 'Only Program Managers can edit savings records.')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    record = get_object_or_404(SavingsRecord, id=record_id, bsg=savings_group)

    if request.method == 'POST':
        try:
            # Capture old values for edit history
            old_amount = record.amount
            old_date = record.savings_date
            old_notes = record.notes

            new_amount_str = request.POST.get('amount', '0').replace(',', '').strip()
            new_amount = Decimal(new_amount_str)
            new_date = request.POST.get('savings_date') or record.savings_date
            new_notes = request.POST.get('notes', record.notes)
            edit_reason = request.POST.get('edit_reason', '').strip()

            if new_amount < 0:
                messages.error(request, 'Amount cannot be negative.')
            elif new_amount > Decimal('99999999.99'):
                messages.error(request, 'Amount is too large.')
            else:
                # Build edit history entry
                changes = []
                if old_amount != new_amount:
                    changes.append(f"Amount: KES {old_amount} → KES {new_amount}")
                if str(old_date) != str(new_date):
                    changes.append(f"Date: {old_date} → {new_date}")
                if old_notes != new_notes:
                    changes.append(f"Notes updated")

                if changes:
                    # Create edit history entry
                    edit_entry = f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] Edited by {user.get_full_name() or user.username}:\n"
                    edit_entry += "  Changes: " + "; ".join(changes) + "\n"
                    if edit_reason:
                        edit_entry += f"  Reason: {edit_reason}\n"

                    # Append to existing edit history
                    record.edit_history = (record.edit_history or "") + edit_entry

                # Update the record
                record.amount = new_amount
                record.savings_date = new_date
                record.notes = new_notes
                record.edited_by = user
                record.edited_at = timezone.now()
                record.save()

                # Update member's total savings
                member = record.member
                difference = new_amount - old_amount
                member.total_savings = (member.total_savings or Decimal('0')) + difference
                member.save()

                # Update group's total savings
                total_savings = savings_group.bsg_members.filter(is_active=True).aggregate(
                    total=Sum('total_savings'))['total'] or Decimal('0')
                savings_group.savings_to_date = total_savings
                savings_group.save()

                messages.success(request, f'Savings record updated successfully!')
                return redirect('savings_groups:savings_report', pk=pk)

        except (ValueError, InvalidOperation):
            messages.error(request, 'Invalid amount format.')

    context = {
        'savings_group': savings_group,
        'record': record,
        'page_title': f'Edit Savings Record - {savings_group.name}',
    }
    return render(request, 'savings_groups/edit_savings_record.html', context)


@login_required
def delete_savings_record(request, pk, record_id):
    """Delete a savings record - ONLY PM and ICT Admin can delete"""
    user = request.user

    if not can_edit_savings(user):
        messages.error(request, 'Only Program Managers can delete savings records.')
        return redirect('savings_groups:savings_group_detail', pk=pk)

    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    record = get_object_or_404(SavingsRecord, id=record_id, bsg=savings_group)

    if request.method == 'POST':
        amount = record.amount
        member = record.member

        # Delete the record
        record.delete()

        # Update member's total savings
        member.total_savings = (member.total_savings or Decimal('0')) - amount
        if member.total_savings < 0:
            member.total_savings = Decimal('0')
        member.save()

        # Update group's total savings
        total_savings = savings_group.bsg_members.filter(is_active=True).aggregate(
            total=Sum('total_savings'))['total'] or Decimal('0')
        savings_group.savings_to_date = total_savings
        savings_group.save()

        messages.success(request, 'Savings record deleted successfully.')
        return redirect('savings_groups:savings_report', pk=pk)

    context = {
        'savings_group': savings_group,
        'record': record,
        'page_title': f'Delete Savings Record - {savings_group.name}',
    }
    return render(request, 'savings_groups/delete_savings_record_confirm.html', context)


# =============================================================================
# LOAN MANAGEMENT VIEWS
# =============================================================================

@login_required
def all_active_loans(request):
    """View all active loans across all savings groups with filtering"""
    from django.utils import timezone

    user = request.user

    # Get accessible savings groups based on role
    if user.role in ['mentor', 'field_associate'] and not user.is_superuser:
        accessible_villages = get_user_accessible_villages(user)
        if accessible_villages.exists():
            savings_groups = BusinessSavingsGroup.objects.filter(
                Q(is_active=True, bsg_members__household__village__in=accessible_villages) |
                Q(created_by=user)
            ).distinct()
        else:
            savings_groups = BusinessSavingsGroup.objects.filter(created_by=user)
    else:
        savings_groups = BusinessSavingsGroup.objects.filter(is_active=True)

    # Get all loans from accessible groups
    all_loans = BSGLoan.objects.filter(bsg__in=savings_groups).select_related(
        'member', 'member__household', 'bsg'
    ).order_by('-loan_date')

    # Filter by status
    status_filter = request.GET.get('status', '')
    loan_type_filter = request.GET.get('loan_type', '')  # 'good' or 'bad'

    if status_filter:
        all_loans = all_loans.filter(status=status_filter)

    # Separate good and bad loans
    today = timezone.now().date()
    good_loans = []
    bad_loans = []
    processed_loans = []

    for loan in all_loans:
        # Calculate days until due or days overdue
        if loan.status == 'fully_repaid':
            loan.days_status = 'Fully Repaid'
            loan.loan_status_type = 'good'
            good_loans.append(loan)
        elif loan.status == 'defaulted':
            loan.days_status = 'Defaulted'
            loan.loan_status_type = 'bad'
            bad_loans.append(loan)
        elif loan.due_date < today:
            days_overdue = (today - loan.due_date).days
            loan.days_status = f'{days_overdue} days overdue'
            loan.loan_status_type = 'bad'
            bad_loans.append(loan)
        else:
            days_remaining = (loan.due_date - today).days
            loan.days_status = f'{days_remaining} days remaining'
            loan.loan_status_type = 'good'
            good_loans.append(loan)

        processed_loans.append(loan)

    # Apply loan type filter
    if loan_type_filter == 'good':
        display_loans = good_loans
    elif loan_type_filter == 'bad':
        display_loans = bad_loans
    else:
        display_loans = processed_loans

    # Calculate totals
    total_loaned = sum(loan.loan_amount for loan in processed_loans if loan.status in ['active', 'partially_repaid', 'fully_repaid'])
    total_outstanding = sum(loan.balance for loan in processed_loans if loan.status in ['active', 'partially_repaid'])

    context = {
        'loans': display_loans,
        'good_loans': good_loans,
        'bad_loans': bad_loans,
        'good_loans_count': len(good_loans),
        'bad_loans_count': len(bad_loans),
        'total_loans': len(processed_loans),
        'total_loaned': total_loaned,
        'total_outstanding': total_outstanding,
        'status_filter': status_filter,
        'loan_type_filter': loan_type_filter,
        'status_choices': BSGLoan.LOAN_STATUS_CHOICES,
        'page_title': 'All Active Loans',
    }
    return render(request, 'savings_groups/all_active_loans.html', context)


@login_required
def loan_list(request, pk):
    """View all loans for a savings group"""
    from django.utils import timezone

    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    all_loans = BSGLoan.objects.filter(bsg=savings_group).order_by('-loan_date')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        loans = all_loans.filter(status=status_filter)
    else:
        loans = all_loans

    # Separate good and bad loans
    today = timezone.now().date()
    good_loans = []  # On track or fully repaid
    bad_loans = []   # Overdue or defaulted

    for loan in loans:
        # Calculate days until due or days overdue
        if loan.status == 'fully_repaid':
            loan.days_status = 'Fully Repaid'
            loan.is_good = True
            good_loans.append(loan)
        elif loan.due_date < today:
            days_overdue = (today - loan.due_date).days
            loan.days_status = f'{days_overdue} days overdue'
            loan.is_good = False
            bad_loans.append(loan)
        else:
            days_remaining = (loan.due_date - today).days
            loan.days_status = f'{days_remaining} days remaining'
            loan.is_good = True
            good_loans.append(loan)

    # Calculate summary
    total_loaned = all_loans.filter(status__in=['active', 'partially_repaid', 'fully_repaid']).aggregate(
        total=Sum('loan_amount'))['total'] or Decimal('0')
    total_repaid = all_loans.aggregate(total=Sum('amount_repaid'))['total'] or Decimal('0')
    active_loans_count = all_loans.filter(status__in=['active', 'partially_repaid']).count()
    overdue_count = len(bad_loans)
    fully_repaid_count = all_loans.filter(status='fully_repaid').count()

    context = {
        'savings_group': savings_group,
        'loans': loans,
        'good_loans': good_loans,
        'bad_loans': bad_loans,
        'total_loaned': total_loaned,
        'total_repaid': total_repaid,
        'active_loans': active_loans_count,
        'overdue_loans': overdue_count,
        'fully_repaid_count': fully_repaid_count,
        'status_choices': BSGLoan.LOAN_STATUS_CHOICES,
        'status_filter': status_filter,
        'page_title': f'Loans - {savings_group.name}',
    }
    return render(request, 'savings_groups/loan_list.html', context)


@login_required
def issue_loan(request, pk):
    """Record a new loan issued to a BSG member"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)

    if request.method == 'POST':
        member_id = request.POST.get('member')
        loan_amount_str = request.POST.get('loan_amount', '0').replace(',', '').strip()
        interest_rate_str = request.POST.get('interest_rate', '10').strip()
        loan_date = request.POST.get('loan_date') or date.today()
        due_date = request.POST.get('due_date')
        purpose = request.POST.get('purpose', '')
        notes = request.POST.get('notes', '')

        try:
            loan_amount = Decimal(loan_amount_str)
            interest_rate = Decimal(interest_rate_str)

            if loan_amount <= 0:
                messages.error(request, 'Loan amount must be greater than zero.')
            elif loan_amount > savings_group.savings_to_date:
                messages.warning(request, f'Note: Loan amount exceeds current group savings (KES {savings_group.savings_to_date:,.2f}).')

            if not member_id:
                messages.error(request, 'Please select a member.')
            elif not due_date:
                messages.error(request, 'Please set a due date.')
            elif loan_amount > 0 and member_id and due_date:
                member = get_object_or_404(BSGMember, id=member_id, bsg=savings_group)

                loan = BSGLoan.objects.create(
                    bsg=savings_group,
                    member=member,
                    loan_amount=loan_amount,
                    interest_rate=interest_rate,
                    loan_date=loan_date,
                    due_date=due_date,
                    purpose=purpose,
                    notes=notes,
                    status='active',
                    recorded_by=request.user
                )

                messages.success(request, f'Loan of KES {loan_amount:,.2f} recorded for {member.household}.')
                return redirect('savings_groups:loan_list', pk=pk)

        except (ValueError, InvalidOperation):
            messages.error(request, 'Invalid amount format.')

    context = {
        'savings_group': savings_group,
        'members': savings_group.bsg_members.filter(is_active=True).order_by('household__head_first_name'),
        'page_title': f'Record Loan - {savings_group.name}',
    }
    return render(request, 'savings_groups/issue_loan.html', context)


@login_required
def approve_loan(request, pk, loan_id):
    """Approve a pending loan - Only PM can approve"""
    user = request.user

    if not can_edit_savings(user):
        messages.error(request, 'Only Program Managers can approve loans.')
        return redirect('savings_groups:loan_list', pk=pk)

    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    loan = get_object_or_404(BSGLoan, id=loan_id, bsg=savings_group)

    if loan.status != 'pending':
        messages.warning(request, 'This loan has already been processed.')
        return redirect('savings_groups:loan_list', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            loan.status = 'disbursed'
            loan.approved_by = user
            loan.approved_date = date.today()
            loan.save()
            messages.success(request, f'Loan of KES {loan.loan_amount:,.2f} approved and disbursed.')
        elif action == 'reject':
            loan.status = 'rejected'
            loan.notes = request.POST.get('notes', '') + f' [Rejected by {user.get_full_name() or user.username}]'
            loan.save()
            messages.info(request, 'Loan application rejected.')

        return redirect('savings_groups:loan_list', pk=pk)

    context = {
        'savings_group': savings_group,
        'loan': loan,
        'page_title': f'Approve Loan - {savings_group.name}',
    }
    return render(request, 'savings_groups/approve_loan.html', context)


@login_required
def loan_detail(request, pk, loan_id):
    """View loan details and repayment history"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    loan = get_object_or_404(BSGLoan, id=loan_id, bsg=savings_group)
    repayments = loan.repayments.order_by('-repayment_date')

    context = {
        'savings_group': savings_group,
        'loan': loan,
        'repayments': repayments,
        'page_title': f'Loan Details - {loan.member.household}',
    }
    return render(request, 'savings_groups/loan_detail.html', context)


@login_required
def record_repayment(request, pk, loan_id):
    """Record a loan repayment"""
    savings_group = get_object_or_404(BusinessSavingsGroup, pk=pk)
    loan = get_object_or_404(BSGLoan, id=loan_id, bsg=savings_group)

    if loan.status not in ['active', 'partially_repaid']:
        messages.warning(request, 'Cannot record repayment for this loan (already fully repaid or defaulted).')
        return redirect('savings_groups:loan_detail', pk=pk, loan_id=loan_id)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '0').replace(',', '').strip()
        repayment_date = request.POST.get('repayment_date') or date.today()
        notes = request.POST.get('notes', '')

        try:
            amount = Decimal(amount_str)

            if amount <= 0:
                messages.error(request, 'Repayment amount must be greater than zero.')
            elif amount > loan.balance:
                messages.warning(request, f'Amount exceeds remaining balance of KES {loan.balance:,.2f}. Recording full balance.')
                amount = loan.balance

            if amount > 0:
                LoanRepayment.objects.create(
                    loan=loan,
                    amount=amount,
                    repayment_date=repayment_date,
                    recorded_by=request.user,
                    notes=notes
                )

                messages.success(request, f'Repayment of KES {amount:,.2f} recorded successfully.')
                return redirect('savings_groups:loan_detail', pk=pk, loan_id=loan_id)

        except (ValueError, InvalidOperation):
            messages.error(request, 'Invalid amount format.')

    context = {
        'savings_group': savings_group,
        'loan': loan,
        'page_title': f'Record Repayment - {loan.member.household}',
    }
    return render(request, 'savings_groups/record_repayment.html', context)
