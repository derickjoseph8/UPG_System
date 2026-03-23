"""
Location Management Views
Handles CRUD operations for Counties, SubCounties, Wards, and Villages
Hierarchy: County → SubCounty → Ward → Village
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.core.paginator import Paginator

from core.models import County, SubCounty, Ward, Village
from .models import SystemAuditLog


# =============================================================================
# Location Management Dashboard
# =============================================================================

@login_required
def location_management(request):
    """Location management dashboard"""
    # Check permissions - only ICT admin and superuser can manage locations
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to manage locations.')
        return redirect('settings:settings_dashboard')

    # Get statistics
    county_count = County.objects.count()
    subcounty_count = SubCounty.objects.count()
    ward_count = Ward.objects.count()
    village_count = Village.objects.count()

    # Get counties with counts
    counties = County.objects.annotate(
        subcounty_count=Count('subcounties', distinct=True),
        ward_count=Count('subcounties__wards', distinct=True),
        village_count=Count('subcounties__wards__villages', distinct=True)
    ).order_by('name')

    context = {
        'page_title': 'Location Management',
        'county_count': county_count,
        'subcounty_count': subcounty_count,
        'ward_count': ward_count,
        'village_count': village_count,
        'counties': counties,
    }
    return render(request, 'settings_module/location_management.html', context)


# =============================================================================
# County Management
# =============================================================================

@login_required
def county_list(request):
    """List all counties"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to manage counties.')
        return redirect('settings:settings_dashboard')

    counties = County.objects.annotate(
        subcounty_count=Count('subcounties', distinct=True),
        ward_count=Count('subcounties__wards', distinct=True),
        village_count=Count('subcounties__wards__villages', distinct=True)
    ).order_by('name')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        counties = counties.filter(name__icontains=search_query)

    # Pagination
    paginator = Paginator(counties, 20)
    page_number = request.GET.get('page')
    counties = paginator.get_page(page_number)

    context = {
        'page_title': 'Counties',
        'counties': counties,
        'search_query': search_query,
    }
    return render(request, 'settings_module/county_list.html', context)


@login_required
def county_create(request):
    """Create a new county"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to create counties.')
        return redirect('settings:county_list')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        country = request.POST.get('country', 'Kenya').strip()

        if not name:
            messages.error(request, 'County name is required.')
        elif County.objects.filter(name__iexact=name).exists():
            messages.error(request, f'A county with the name "{name}" already exists.')
        else:
            try:
                county = County.objects.create(
                    name=name,
                    country=country
                )

                # Log the action
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='create',
                    model_name='County',
                    object_id=str(county.id),
                    object_repr=str(county),
                    success=True
                )

                messages.success(request, f'County "{name}" created successfully!')
                return redirect('settings:county_list')

            except Exception as e:
                messages.error(request, f'Error creating county: {str(e)}')

    context = {
        'page_title': 'Create County',
        'form_action': 'create',
    }
    return render(request, 'settings_module/county_form.html', context)


@login_required
def county_edit(request, county_id):
    """Edit a county"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to edit counties.')
        return redirect('settings:county_list')

    county = get_object_or_404(County, id=county_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        country = request.POST.get('country', 'Kenya').strip()

        if not name:
            messages.error(request, 'County name is required.')
        elif County.objects.filter(name__iexact=name).exclude(id=county_id).exists():
            messages.error(request, f'A county with the name "{name}" already exists.')
        else:
            try:
                old_name = county.name
                county.name = name
                county.country = country
                county.save()

                # Log the action
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='County',
                    object_id=str(county.id),
                    object_repr=str(county),
                    changes={'old_name': old_name, 'new_name': name},
                    success=True
                )

                messages.success(request, f'County "{name}" updated successfully!')
                return redirect('settings:county_list')

            except Exception as e:
                messages.error(request, f'Error updating county: {str(e)}')

    context = {
        'page_title': f'Edit County - {county.name}',
        'county': county,
        'form_action': 'edit',
    }
    return render(request, 'settings_module/county_form.html', context)


@login_required
@require_POST
def county_delete(request, county_id):
    """Delete a county"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    county = get_object_or_404(County, id=county_id)

    # Check if county has subcounties
    subcounty_count = county.subcounties.count()
    if subcounty_count > 0:
        return JsonResponse({
            'success': False,
            'message': f'Cannot delete county "{county.name}". It has {subcounty_count} sub-county(ies). Delete the sub-counties first.'
        })

    try:
        county_name = county.name
        county_id_str = str(county.id)

        # Log the action before deletion
        SystemAuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='County',
            object_id=county_id_str,
            object_repr=county_name,
            success=True
        )

        county.delete()

        return JsonResponse({
            'success': True,
            'message': f'County "{county_name}" deleted successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting county: {str(e)}'
        }, status=500)


# =============================================================================
# SubCounty Management
# =============================================================================

@login_required
def subcounty_list(request):
    """List all subcounties"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to manage sub-counties.')
        return redirect('settings:settings_dashboard')

    subcounties = SubCounty.objects.select_related('county').annotate(
        ward_count=Count('wards', distinct=True),
        village_count=Count('wards__villages', distinct=True)
    ).order_by('county__name', 'name')

    # Filter by county
    county_filter = request.GET.get('county')
    if county_filter:
        subcounties = subcounties.filter(county_id=county_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        subcounties = subcounties.filter(
            Q(name__icontains=search_query) |
            Q(county__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(subcounties, 20)
    page_number = request.GET.get('page')
    subcounties = paginator.get_page(page_number)

    # Get all counties for filter dropdown
    counties = County.objects.all().order_by('name')

    context = {
        'page_title': 'Sub-Counties',
        'subcounties': subcounties,
        'counties': counties,
        'search_query': search_query,
        'selected_county': county_filter,
    }
    return render(request, 'settings_module/subcounty_list.html', context)


@login_required
def subcounty_create(request):
    """Create a new subcounty"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to create sub-counties.')
        return redirect('settings:subcounty_list')

    counties = County.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        county_id = request.POST.get('county')

        if not name:
            messages.error(request, 'Sub-county name is required.')
        elif not county_id:
            messages.error(request, 'Please select a county.')
        else:
            try:
                county = County.objects.get(id=county_id)

                # Check if subcounty already exists in this county
                if SubCounty.objects.filter(name__iexact=name, county=county).exists():
                    messages.error(request, f'A sub-county named "{name}" already exists in {county.name}.')
                else:
                    subcounty = SubCounty.objects.create(
                        name=name,
                        county=county
                    )

                    # Log the action
                    SystemAuditLog.objects.create(
                        user=request.user,
                        action='create',
                        model_name='SubCounty',
                        object_id=str(subcounty.id),
                        object_repr=str(subcounty),
                        success=True
                    )

                    messages.success(request, f'Sub-county "{name}" created successfully!')
                    return redirect('settings:subcounty_list')

            except County.DoesNotExist:
                messages.error(request, 'Selected county does not exist.')
            except Exception as e:
                messages.error(request, f'Error creating sub-county: {str(e)}')

    # Pre-select county if provided in URL
    preselect_county = request.GET.get('county')

    context = {
        'page_title': 'Create Sub-County',
        'counties': counties,
        'form_action': 'create',
        'preselect_county': preselect_county,
    }
    return render(request, 'settings_module/subcounty_form.html', context)


@login_required
def subcounty_edit(request, subcounty_id):
    """Edit a subcounty"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to edit sub-counties.')
        return redirect('settings:subcounty_list')

    subcounty = get_object_or_404(SubCounty, id=subcounty_id)
    counties = County.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        county_id = request.POST.get('county')

        if not name:
            messages.error(request, 'Sub-county name is required.')
        elif not county_id:
            messages.error(request, 'Please select a county.')
        else:
            try:
                county = County.objects.get(id=county_id)

                # Check if subcounty already exists in this county (excluding current)
                if SubCounty.objects.filter(name__iexact=name, county=county).exclude(id=subcounty_id).exists():
                    messages.error(request, f'A sub-county named "{name}" already exists in {county.name}.')
                else:
                    old_name = subcounty.name
                    subcounty.name = name
                    subcounty.county = county
                    subcounty.save()

                    # Log the action
                    SystemAuditLog.objects.create(
                        user=request.user,
                        action='update',
                        model_name='SubCounty',
                        object_id=str(subcounty.id),
                        object_repr=str(subcounty),
                        changes={'old_name': old_name, 'new_name': name},
                        success=True
                    )

                    messages.success(request, f'Sub-county "{name}" updated successfully!')
                    return redirect('settings:subcounty_list')

            except County.DoesNotExist:
                messages.error(request, 'Selected county does not exist.')
            except Exception as e:
                messages.error(request, f'Error updating sub-county: {str(e)}')

    context = {
        'page_title': f'Edit Sub-County - {subcounty.name}',
        'subcounty': subcounty,
        'counties': counties,
        'form_action': 'edit',
    }
    return render(request, 'settings_module/subcounty_form.html', context)


@login_required
@require_POST
def subcounty_delete(request, subcounty_id):
    """Delete a subcounty"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    subcounty = get_object_or_404(SubCounty, id=subcounty_id)

    # Check if subcounty has wards
    ward_count = subcounty.wards.count()
    if ward_count > 0:
        return JsonResponse({
            'success': False,
            'message': f'Cannot delete sub-county "{subcounty.name}". It has {ward_count} ward(s). Delete the wards first.'
        })

    try:
        subcounty_name = str(subcounty)
        subcounty_id_str = str(subcounty.id)

        # Log the action before deletion
        SystemAuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='SubCounty',
            object_id=subcounty_id_str,
            object_repr=subcounty_name,
            success=True
        )

        subcounty.delete()

        return JsonResponse({
            'success': True,
            'message': f'Sub-county "{subcounty_name}" deleted successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting sub-county: {str(e)}'
        }, status=500)


# =============================================================================
# Ward Management
# =============================================================================

@login_required
def ward_list(request):
    """List all wards"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to manage wards.')
        return redirect('settings:settings_dashboard')

    wards = Ward.objects.select_related('subcounty', 'subcounty__county').annotate(
        village_count=Count('villages')
    ).order_by('subcounty__county__name', 'subcounty__name', 'name')

    # Filter by county
    county_filter = request.GET.get('county')
    if county_filter:
        wards = wards.filter(subcounty__county_id=county_filter)

    # Filter by subcounty
    subcounty_filter = request.GET.get('subcounty')
    if subcounty_filter:
        wards = wards.filter(subcounty_id=subcounty_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        wards = wards.filter(
            Q(name__icontains=search_query) |
            Q(subcounty__name__icontains=search_query) |
            Q(subcounty__county__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(wards, 25)
    page_number = request.GET.get('page')
    wards = paginator.get_page(page_number)

    # Get counties and subcounties for filter dropdowns
    counties = County.objects.all().order_by('name')
    subcounties = SubCounty.objects.select_related('county').order_by('county__name', 'name')

    context = {
        'page_title': 'Wards',
        'wards': wards,
        'counties': counties,
        'subcounties': subcounties,
        'search_query': search_query,
        'selected_county': county_filter,
        'selected_subcounty': subcounty_filter,
    }
    return render(request, 'settings_module/ward_list.html', context)


@login_required
def ward_create(request):
    """Create a new ward"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to create wards.')
        return redirect('settings:ward_list')

    counties = County.objects.all().order_by('name')
    subcounties = SubCounty.objects.select_related('county').order_by('county__name', 'name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        subcounty_id = request.POST.get('subcounty')

        if not name:
            messages.error(request, 'Ward name is required.')
        elif not subcounty_id:
            messages.error(request, 'Please select a sub-county.')
        else:
            try:
                subcounty = SubCounty.objects.get(id=subcounty_id)

                # Check if ward already exists in this subcounty
                if Ward.objects.filter(name__iexact=name, subcounty=subcounty).exists():
                    messages.error(request, f'A ward named "{name}" already exists in {subcounty.name}.')
                else:
                    ward = Ward.objects.create(
                        name=name,
                        subcounty=subcounty
                    )

                    # Log the action
                    SystemAuditLog.objects.create(
                        user=request.user,
                        action='create',
                        model_name='Ward',
                        object_id=str(ward.id),
                        object_repr=str(ward),
                        success=True
                    )

                    messages.success(request, f'Ward "{name}" created successfully!')
                    return redirect('settings:ward_list')

            except SubCounty.DoesNotExist:
                messages.error(request, 'Selected sub-county does not exist.')
            except Exception as e:
                messages.error(request, f'Error creating ward: {str(e)}')

    # Pre-select subcounty if provided in URL
    preselect_subcounty = request.GET.get('subcounty')

    context = {
        'page_title': 'Create Ward',
        'counties': counties,
        'subcounties': subcounties,
        'form_action': 'create',
        'preselect_subcounty': preselect_subcounty,
    }
    return render(request, 'settings_module/ward_form.html', context)


@login_required
def ward_edit(request, ward_id):
    """Edit a ward"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to edit wards.')
        return redirect('settings:ward_list')

    ward = get_object_or_404(Ward, id=ward_id)
    counties = County.objects.all().order_by('name')
    subcounties = SubCounty.objects.select_related('county').order_by('county__name', 'name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        subcounty_id = request.POST.get('subcounty')

        if not name:
            messages.error(request, 'Ward name is required.')
        elif not subcounty_id:
            messages.error(request, 'Please select a sub-county.')
        else:
            try:
                subcounty = SubCounty.objects.get(id=subcounty_id)

                # Check if ward already exists in this subcounty (excluding current)
                if Ward.objects.filter(name__iexact=name, subcounty=subcounty).exclude(id=ward_id).exists():
                    messages.error(request, f'A ward named "{name}" already exists in {subcounty.name}.')
                else:
                    old_name = ward.name
                    ward.name = name
                    ward.subcounty = subcounty
                    ward.save()

                    # Log the action
                    SystemAuditLog.objects.create(
                        user=request.user,
                        action='update',
                        model_name='Ward',
                        object_id=str(ward.id),
                        object_repr=str(ward),
                        changes={'old_name': old_name, 'new_name': name},
                        success=True
                    )

                    messages.success(request, f'Ward "{name}" updated successfully!')
                    return redirect('settings:ward_list')

            except SubCounty.DoesNotExist:
                messages.error(request, 'Selected sub-county does not exist.')
            except Exception as e:
                messages.error(request, f'Error updating ward: {str(e)}')

    context = {
        'page_title': f'Edit Ward - {ward.name}',
        'ward': ward,
        'counties': counties,
        'subcounties': subcounties,
        'form_action': 'edit',
    }
    return render(request, 'settings_module/ward_form.html', context)


@login_required
@require_POST
def ward_delete(request, ward_id):
    """Delete a ward"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    ward = get_object_or_404(Ward, id=ward_id)

    # Check if ward has villages
    village_count = ward.villages.count()
    if village_count > 0:
        return JsonResponse({
            'success': False,
            'message': f'Cannot delete ward "{ward.name}". It has {village_count} village(s). Delete the villages first.'
        })

    try:
        ward_name = str(ward)
        ward_id_str = str(ward.id)

        # Log the action before deletion
        SystemAuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Ward',
            object_id=ward_id_str,
            object_repr=ward_name,
            success=True
        )

        ward.delete()

        return JsonResponse({
            'success': True,
            'message': f'Ward "{ward_name}" deleted successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting ward: {str(e)}'
        }, status=500)


# =============================================================================
# Village Management
# =============================================================================

@login_required
def village_list(request):
    """List all villages"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to manage villages.')
        return redirect('settings:settings_dashboard')

    villages = Village.objects.select_related(
        'ward', 'ward__subcounty', 'ward__subcounty__county'
    ).order_by('ward__subcounty__county__name', 'ward__subcounty__name', 'ward__name', 'name')

    # Filter by county
    county_filter = request.GET.get('county')
    if county_filter:
        villages = villages.filter(ward__subcounty__county_id=county_filter)

    # Filter by subcounty
    subcounty_filter = request.GET.get('subcounty')
    if subcounty_filter:
        villages = villages.filter(ward__subcounty_id=subcounty_filter)

    # Filter by ward
    ward_filter = request.GET.get('ward')
    if ward_filter:
        villages = villages.filter(ward_id=ward_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        villages = villages.filter(
            Q(name__icontains=search_query) |
            Q(ward__name__icontains=search_query) |
            Q(ward__subcounty__name__icontains=search_query) |
            Q(ward__subcounty__county__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(villages, 25)
    page_number = request.GET.get('page')
    villages = paginator.get_page(page_number)

    # Get filter dropdown data
    counties = County.objects.all().order_by('name')
    subcounties = SubCounty.objects.select_related('county').order_by('county__name', 'name')
    wards = Ward.objects.select_related('subcounty', 'subcounty__county').order_by(
        'subcounty__county__name', 'subcounty__name', 'name'
    )

    context = {
        'page_title': 'Villages',
        'villages': villages,
        'counties': counties,
        'subcounties': subcounties,
        'wards': wards,
        'search_query': search_query,
        'selected_county': county_filter,
        'selected_subcounty': subcounty_filter,
        'selected_ward': ward_filter,
    }
    return render(request, 'settings_module/village_list.html', context)


@login_required
def village_create(request):
    """Create a new village"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to create villages.')
        return redirect('settings:village_list')

    counties = County.objects.all().order_by('name')
    subcounties = SubCounty.objects.select_related('county').order_by('county__name', 'name')
    wards = Ward.objects.select_related('subcounty', 'subcounty__county').order_by(
        'subcounty__county__name', 'subcounty__name', 'name'
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        ward_id = request.POST.get('ward')
        is_program_area = request.POST.get('is_program_area') == 'on'
        distance_to_market = request.POST.get('distance_to_market', 0)
        saturation = request.POST.get('saturation', '').strip()

        if not name:
            messages.error(request, 'Village name is required.')
        elif not ward_id:
            messages.error(request, 'Please select a ward.')
        else:
            try:
                ward = Ward.objects.get(id=ward_id)

                village = Village.objects.create(
                    name=name,
                    ward=ward,
                    is_program_area=is_program_area,
                    distance_to_market=int(distance_to_market) if distance_to_market else 0,
                    saturation=saturation
                )

                # Log the action
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='create',
                    model_name='Village',
                    object_id=str(village.id),
                    object_repr=str(village),
                    success=True
                )

                messages.success(request, f'Village "{name}" created successfully!')
                return redirect('settings:village_list')

            except Ward.DoesNotExist:
                messages.error(request, 'Selected ward does not exist.')
            except Exception as e:
                messages.error(request, f'Error creating village: {str(e)}')

    # Pre-select ward if provided in URL
    preselect_ward = request.GET.get('ward')

    context = {
        'page_title': 'Create Village',
        'counties': counties,
        'subcounties': subcounties,
        'wards': wards,
        'form_action': 'create',
        'preselect_ward': preselect_ward,
    }
    return render(request, 'settings_module/village_form.html', context)


@login_required
def village_edit(request, village_id):
    """Edit a village"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        messages.error(request, 'You do not have permission to edit villages.')
        return redirect('settings:village_list')

    village = get_object_or_404(Village, id=village_id)
    counties = County.objects.all().order_by('name')
    subcounties = SubCounty.objects.select_related('county').order_by('county__name', 'name')
    wards = Ward.objects.select_related('subcounty', 'subcounty__county').order_by(
        'subcounty__county__name', 'subcounty__name', 'name'
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        ward_id = request.POST.get('ward')
        is_program_area = request.POST.get('is_program_area') == 'on'
        distance_to_market = request.POST.get('distance_to_market', 0)
        saturation = request.POST.get('saturation', '').strip()

        if not name:
            messages.error(request, 'Village name is required.')
        elif not ward_id:
            messages.error(request, 'Please select a ward.')
        else:
            try:
                ward = Ward.objects.get(id=ward_id)

                old_name = village.name
                village.name = name
                village.ward = ward
                village.is_program_area = is_program_area
                village.distance_to_market = int(distance_to_market) if distance_to_market else 0
                village.saturation = saturation
                village.save()

                # Log the action
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='Village',
                    object_id=str(village.id),
                    object_repr=str(village),
                    changes={'old_name': old_name, 'new_name': name},
                    success=True
                )

                messages.success(request, f'Village "{name}" updated successfully!')
                return redirect('settings:village_list')

            except Ward.DoesNotExist:
                messages.error(request, 'Selected ward does not exist.')
            except Exception as e:
                messages.error(request, f'Error updating village: {str(e)}')

    context = {
        'page_title': f'Edit Village - {village.name}',
        'village': village,
        'counties': counties,
        'subcounties': subcounties,
        'wards': wards,
        'form_action': 'edit',
    }
    return render(request, 'settings_module/village_form.html', context)


@login_required
@require_POST
def village_delete(request, village_id):
    """Delete a village"""
    if not (request.user.is_superuser or request.user.role in ['ict_admin', 'program_manager']):
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)

    village = get_object_or_404(Village, id=village_id)

    try:
        village_name = str(village)
        village_id_str = str(village.id)

        # Log the action before deletion
        SystemAuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Village',
            object_id=village_id_str,
            object_repr=village_name,
            success=True
        )

        village.delete()

        return JsonResponse({
            'success': True,
            'message': f'Village "{village_name}" deleted successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting village: {str(e)}'
        }, status=500)


# =============================================================================
# AJAX Endpoints for Dynamic Dropdowns
# =============================================================================

@login_required
def get_subcounties_by_county(request):
    """AJAX endpoint to get subcounties by county"""
    county_id = request.GET.get('county_id')
    if county_id:
        subcounties = SubCounty.objects.filter(county_id=county_id).order_by('name')
        data = [{'id': sc.id, 'name': sc.name} for sc in subcounties]
        return JsonResponse({'subcounties': data})
    return JsonResponse({'subcounties': []})


@login_required
def get_wards_by_subcounty(request):
    """AJAX endpoint to get wards by subcounty"""
    subcounty_id = request.GET.get('subcounty_id')
    if subcounty_id:
        wards = Ward.objects.filter(subcounty_id=subcounty_id).order_by('name')
        data = [{'id': w.id, 'name': w.name} for w in wards]
        return JsonResponse({'wards': data})
    return JsonResponse({'wards': []})


@login_required
def get_villages_by_ward(request):
    """AJAX endpoint to get villages by ward"""
    ward_id = request.GET.get('ward_id')
    if ward_id:
        villages = Village.objects.filter(ward_id=ward_id).order_by('name')
        data = [{'id': v.id, 'name': v.name} for v in villages]
        return JsonResponse({'villages': data})
    return JsonResponse({'villages': []})
