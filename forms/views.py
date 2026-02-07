from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
import json

from .models import (
    FormTemplate, FormAssignment, FormSubmission, FormField,
    FormAssignmentMentor, KoboSyncLog, KoboWebhookLog,
    FormFieldAssociate, FormMentorAssignment
)
from core.models import Village
from households.models import Household
from business_groups.models import BusinessGroup

User = get_user_model()

@login_required
def forms_dashboard(request):
    """Main forms dashboard showing different views based on user role"""
    user = request.user
    user_role = getattr(user, 'role', None)
    context = {
        'page_title': 'Dynamic Forms Dashboard',
        'user_role': user_role,
    }

    if user.is_superuser or user_role in ['me_staff', 'ict_admin']:
        # M&E/Admin view - can create and manage all forms
        form_templates = FormTemplate.objects.all()[:10]
        recent_assignments = FormAssignment.objects.all()[:5]
        recent_submissions = FormSubmission.objects.all()[:10]

        context.update({
            'can_create_forms': True,
            'can_manage_all': True,
            'form_templates': form_templates,
            'recent_assignments': recent_assignments,
            'recent_submissions': recent_submissions,
            'total_templates': FormTemplate.objects.count(),
            'active_assignments': FormAssignment.objects.filter(status__in=['pending', 'accepted', 'in_progress']).count(),
        })

    elif user_role == 'program_manager':
        # PM view - can create forms and assign to FAs
        form_templates = FormTemplate.objects.filter(created_by=user)[:10]
        fa_assignments = FormFieldAssociate.objects.filter(assigned_by=user)[:10]
        recent_submissions = FormSubmission.objects.all()[:10]

        context.update({
            'can_create_forms': True,  # PM can create forms
            'can_assign_to_fa': True,
            'form_templates': form_templates,
            'fa_assignments': fa_assignments,
            'recent_submissions': recent_submissions,
            'total_templates': FormTemplate.objects.filter(created_by=user).count(),
        })

    elif user_role == 'field_associate':
        # FA view - can see forms assigned to them and assign to mentors
        my_fa_assignments = FormFieldAssociate.objects.filter(field_associate=user)
        my_form_ids = my_fa_assignments.values_list('form_template_id', flat=True)
        my_forms = FormTemplate.objects.filter(id__in=my_form_ids)
        my_mentor_assignments = FormMentorAssignment.objects.filter(form_fa__field_associate=user)

        context.update({
            'can_assign_to_mentors': True,
            'my_forms': my_forms,
            'fa_assignments': my_fa_assignments,
            'mentor_assignments': my_mentor_assignments,
            'pending_assignments': my_fa_assignments.filter(status='pending').count(),
        })

    elif user_role == 'mentor':
        # Mentor view - can only see forms assigned to them
        my_mentor_assignment_ids = FormMentorAssignment.objects.filter(
            mentor=user
        ).values_list('form_fa__form_template_id', flat=True)
        my_forms = FormTemplate.objects.filter(id__in=my_mentor_assignment_ids, status='active')
        my_submissions = FormSubmission.objects.filter(submitted_by=user)

        # Also get legacy assignments
        legacy_assignments = FormAssignment.objects.filter(mentor=user)
        legacy_mentor_assignments = FormAssignmentMentor.objects.filter(mentor=user)

        context.update({
            'can_fill_forms': True,
            'my_forms': my_forms,
            'my_submissions': my_submissions,
            'legacy_assignments': legacy_assignments,
            'legacy_mentor_assignments': legacy_mentor_assignments,
            'pending_forms': my_forms.count(),
        })

    return render(request, 'forms/dashboard.html', context)


# ==================== KoboToolbox Integration Views ====================

@login_required
def preview_kobo_form(request, form_template_id):
    """
    Preview form structure before syncing to KoboToolbox.
    Shows the XLSForm structure that will be sent to Kobo.

    Args:
        request: HTTP request
        form_template_id: ID of FormTemplate to preview

    Returns:
        JsonResponse: XLSForm structure or rendered template
    """
    # Permission check
    if request.user.role not in ['me_staff', 'ict_admin', 'program_manager'] and not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to preview forms'
        }, status=403)

    # Get form template
    form_template = get_object_or_404(FormTemplate, id=form_template_id)

    # Import converter
    from .kobo_service import XLSFormConverter

    try:
        # Convert to XLSForm structure
        converter = XLSFormConverter(form_template)
        xlsform_content = converter.convert_to_xlsform()

        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'form_name': form_template.name,
                'form_id': xlsform_content['settings'].get('form_id', ''),
                'version': xlsform_content['settings'].get('version', ''),
                'survey': xlsform_content['survey'],
                'choices': xlsform_content['choices'],
                'settings': xlsform_content['settings'],
                'total_fields': len(xlsform_content['survey']),
                'total_choices': len(xlsform_content['choices']),
            })

        # For regular request, render template
        context = {
            'page_title': f'Preview Form - {form_template.name}',
            'form_template': form_template,
            'xlsform': json.dumps(xlsform_content, indent=2),
            'survey_fields': xlsform_content['survey'],
            'choice_lists': xlsform_content['choices'],
            'settings': xlsform_content['settings'],
        }
        return render(request, 'forms/form_preview.html', context)

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Preview error: {str(e)}'
            }, status=500)
        messages.error(request, f'Error generating preview: {str(e)}')
        return redirect('forms:template_builder', pk=form_template_id)


@login_required
def manual_sync_to_kobo(request, form_template_id):
    """
    Manual sync trigger for syncing a form to KoboToolbox

    Args:
        request: HTTP request
        form_template_id: ID of FormTemplate to sync

    Returns:
        JsonResponse: Success or error message
    """
    # Permission check
    if request.user.role not in ['me_staff', 'ict_admin'] and not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to sync forms'
        }, status=403)

    # Must be POST request
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

    # Get form template
    form_template = get_object_or_404(FormTemplate, id=form_template_id)

    # Check if sync is enabled
    if not form_template.sync_to_kobo:
        return JsonResponse({
            'success': False,
            'message': 'KoboToolbox sync is not enabled for this form'
        }, status=400)

    # Import sync function
    from .kobo_service import sync_form_to_kobo

    # Trigger sync
    try:
        success, message, asset_uid = sync_form_to_kobo(
            form_template,
            user=request.user,
            force=True  # Force sync even if already synced
        )

        return JsonResponse({
            'success': success,
            'message': message,
            'asset_uid': asset_uid,
            'form_url': form_template.kobo_form_url if success else None,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Sync error: {str(e)}'
        }, status=500)


@login_required
def kobo_sync_history(request, form_template_id):
    """
    Display sync history for a specific form

    Args:
        request: HTTP request
        form_template_id: ID of FormTemplate

    Returns:
        Rendered template with sync logs
    """
    # Permission check
    if request.user.role not in ['me_staff', 'ict_admin'] and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to view sync history")

    form_template = get_object_or_404(FormTemplate, id=form_template_id)

    # Get sync logs
    sync_logs = KoboSyncLog.objects.filter(
        form_template=form_template
    ).select_related('initiated_by').order_by('-started_at')

    # Pagination
    paginator = Paginator(sync_logs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': f'Kobo Sync History - {form_template.name}',
        'form_template': form_template,
        'sync_logs': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'forms/sync_history.html', context)


@login_required
def kobo_webhook_logs(request):
    """
    Display webhook logs for incoming submissions from KoboToolbox

    Args:
        request: HTTP request

    Returns:
        Rendered template with webhook logs
    """
    # Permission check
    if request.user.role not in ['me_staff', 'ict_admin'] and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to view webhook logs")

    # Get webhook logs
    webhook_logs = KoboWebhookLog.objects.all().select_related(
        'form_template',
        'form_submission',
        'form_submission__submitted_by'
    ).order_by('-received_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(KoboWebhookLog.STATUS_CHOICES):
        webhook_logs = webhook_logs.filter(status=status_filter)

    # Filter by form template
    form_id = request.GET.get('form_id')
    if form_id:
        webhook_logs = webhook_logs.filter(form_template_id=form_id)

    # Pagination
    paginator = Paginator(webhook_logs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get available forms for filtering
    forms_with_logs = FormTemplate.objects.filter(
        kobo_asset_uid__isnull=False
    ).values_list('id', 'name')

    context = {
        'page_title': 'KoboToolbox Webhook Logs',
        'webhook_logs': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'form_id_filter': form_id,
        'available_forms': forms_with_logs,
        'status_choices': KoboWebhookLog.STATUS_CHOICES,
    }

    return render(request, 'forms/webhook_logs.html', context)


# ==================== Form Template Views ====================

@login_required
def form_template_list(request):
    """List all form templates"""
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin'] and not user.is_superuser:
        messages.error(request, 'You do not have permission to view form templates')
        return redirect('forms:dashboard')

    templates = FormTemplate.objects.all().select_related('created_by').order_by('-created_at')

    context = {
        'page_title': 'Form Templates',
        'templates': templates,
    }

    return render(request, 'forms/template_list.html', context)


@login_required
def form_template_create(request):
    """Create a new form template"""
    user = request.user

    # Permission check - Only PM and M&E can create forms (NOT FA or Mentors)
    if user.role not in ['me_staff', 'ict_admin', 'program_manager'] and not user.is_superuser:
        messages.error(request, 'Only Program Managers and M&E staff can create forms')
        return redirect('forms:dashboard')

    # Get available Field Associates for assignment
    field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')

    context = {
        'page_title': 'Create New Form',
        'form_template': None,
        'field_associates': field_associates,
        'can_assign_fa': user.role in ['program_manager', 'me_staff', 'ict_admin'] or user.is_superuser,
    }

    return render(request, 'forms/template_builder.html', context)


@login_required
def import_form_template(request):
    """Import a form template from JSON or XML file"""
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin'] and not user.is_superuser:
        messages.error(request, 'You do not have permission to import forms')
        return redirect('forms:dashboard')

    if request.method == 'POST':
        try:
            from .form_importer import import_form_from_file

            uploaded_file = request.FILES.get('form_file')
            if not uploaded_file:
                return JsonResponse({
                    'success': False,
                    'message': 'No file uploaded'
                }, status=400)

            # Read file content
            file_content = uploaded_file.read().decode('utf-8')
            filename = uploaded_file.name.lower()

            # Determine file type
            if filename.endswith('.json'):
                file_type = 'json'
            elif filename.endswith('.xml'):
                file_type = 'xml'
            else:
                # Try to detect from content
                file_content_stripped = file_content.strip()
                if file_content_stripped.startswith('{') or file_content_stripped.startswith('['):
                    file_type = 'json'
                elif file_content_stripped.startswith('<'):
                    file_type = 'xml'
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Could not determine file type. Please use .json or .xml extension.'
                    }, status=400)

            # Parse the file
            metadata, fields, errors, warnings = import_form_from_file(file_content, file_type)

            if errors:
                return JsonResponse({
                    'success': False,
                    'message': 'Import errors: ' + '; '.join(errors)
                }, status=400)

            if metadata is None:
                return JsonResponse({
                    'success': False,
                    'message': 'Could not parse form data from file'
                }, status=400)

            # Create form template
            with transaction.atomic():
                form_template = FormTemplate.objects.create(
                    name=metadata.get('name', 'Imported Form'),
                    description=metadata.get('description', ''),
                    form_type=metadata.get('form_type', 'custom_form'),
                    status='draft',
                    form_purpose=metadata.get('form_purpose', 'general'),
                    kobo_asset_uid=metadata.get('kobo_asset_uid', ''),
                    kobo_form_url=metadata.get('kobo_form_url', ''),
                    created_by=user
                )

                # Create form fields
                for field_data in fields:
                    FormField.objects.create(
                        form_template=form_template,
                        field_name=field_data.get('field_name', f'field_{field_data.get("order", 0)}'),
                        field_label=field_data.get('field_label', 'Untitled'),
                        field_type=field_data.get('field_type', 'text'),
                        required=field_data.get('required', False),
                        help_text=field_data.get('help_text', ''),
                        placeholder=field_data.get('placeholder', ''),
                        default_value=field_data.get('default_value', ''),
                        choices=field_data.get('choices', []),
                        min_value=field_data.get('min_value'),
                        max_value=field_data.get('max_value'),
                        min_length=field_data.get('min_length'),
                        max_length=field_data.get('max_length'),
                        show_if_field=field_data.get('show_if_field', ''),
                        show_if_value=field_data.get('show_if_value', ''),
                        order=field_data.get('order', 0)
                    )

                # Also store fields in JSONField as backup
                form_template.form_fields = fields
                form_template.save()

            response_data = {
                'success': True,
                'message': f'Form "{form_template.name}" imported successfully with {len(fields)} fields!',
                'form_id': form_template.id,
                'redirect_url': f'/forms/templates/{form_template.id}/builder/'
            }

            if warnings:
                response_data['warnings'] = warnings

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error importing form: {str(e)}'
            }, status=500)

    # GET request - show import page
    context = {
        'page_title': 'Import Form Template',
    }
    return render(request, 'forms/import_form.html', context)


@login_required
def import_from_kobo(request):
    """Import a form directly from KoboToolbox account"""
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin'] and not user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to import forms'
        }, status=403)

    if request.method == 'POST':
        try:
            from .form_importer import FormImporter
            from .kobo_service import KoboAPIClient

            data = json.loads(request.body)
            asset_uid = data.get('asset_uid')

            if not asset_uid:
                return JsonResponse({
                    'success': False,
                    'message': 'Asset UID is required'
                }, status=400)

            # Fetch asset from Kobo
            client = KoboAPIClient()
            asset_data = client.get_asset(asset_uid)

            # Parse the asset
            importer = FormImporter()
            metadata, fields = importer.import_from_kobo_asset(asset_data)

            if importer.errors:
                return JsonResponse({
                    'success': False,
                    'message': 'Import errors: ' + '; '.join(importer.errors)
                }, status=400)

            # Check if form with this UID already exists
            existing = FormTemplate.objects.filter(kobo_asset_uid=asset_uid).first()
            if existing:
                return JsonResponse({
                    'success': False,
                    'message': f'A form with this Kobo asset already exists: "{existing.name}" (ID: {existing.id})'
                }, status=400)

            # Create form template
            with transaction.atomic():
                form_template = FormTemplate.objects.create(
                    name=metadata.get('name', 'Imported Form'),
                    description=metadata.get('description', ''),
                    form_type='custom_form',
                    status='draft',
                    sync_to_kobo=True,
                    kobo_asset_uid=asset_uid,
                    kobo_form_url=metadata.get('kobo_form_url', ''),
                    kobo_sync_status='synced',
                    last_synced_at=timezone.now(),
                    created_by=user
                )

                # Create form fields
                for field_data in fields:
                    FormField.objects.create(
                        form_template=form_template,
                        field_name=field_data.get('field_name', f'field_{field_data.get("order", 0)}'),
                        field_label=field_data.get('field_label', 'Untitled'),
                        field_type=field_data.get('field_type', 'text'),
                        required=field_data.get('required', False),
                        help_text=field_data.get('help_text', ''),
                        placeholder=field_data.get('placeholder', ''),
                        default_value=field_data.get('default_value', ''),
                        choices=field_data.get('choices', []),
                        min_value=field_data.get('min_value'),
                        max_value=field_data.get('max_value'),
                        min_length=field_data.get('min_length'),
                        max_length=field_data.get('max_length'),
                        show_if_field=field_data.get('show_if_field', ''),
                        show_if_value=field_data.get('show_if_value', ''),
                        order=field_data.get('order', 0)
                    )

                form_template.form_fields = fields
                form_template.save()

            return JsonResponse({
                'success': True,
                'message': f'Form "{form_template.name}" imported from KoboToolbox with {len(fields)} fields!',
                'form_id': form_template.id,
                'redirect_url': f'/forms/templates/{form_template.id}/builder/'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error importing from Kobo: {str(e)}'
            }, status=500)

    # GET request - list available Kobo forms
    try:
        from .kobo_service import KoboAPIClient
        import requests

        client = KoboAPIClient()
        url = f"{client.api_url}/assets/"
        params = {'asset_type': 'survey', 'limit': 100}

        response = requests.get(url, headers=client.headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        assets = data.get('results', [])

        # Filter out already imported assets
        imported_uids = set(FormTemplate.objects.filter(
            kobo_asset_uid__isnull=False
        ).exclude(kobo_asset_uid='').values_list('kobo_asset_uid', flat=True))

        available_assets = [
            {
                'uid': asset.get('uid'),
                'name': asset.get('name'),
                'date_created': asset.get('date_created'),
                'deployment_status': asset.get('deployment__active', False),
                'submissions_count': asset.get('deployment__submission_count', 0),
                'already_imported': asset.get('uid') in imported_uids,
            }
            for asset in assets
        ]

        return JsonResponse({
            'success': True,
            'assets': available_assets
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching Kobo forms: {str(e)}'
        }, status=500)


@login_required
def save_form_template(request):
    """Save form template via AJAX (create or update)"""
    user = request.user

    # Permission check - Only PM and M&E can save forms (NOT FA or Mentors)
    if user.role not in ['me_staff', 'ict_admin', 'program_manager'] and not user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'Only Program Managers and M&E staff can create/edit forms'
        }, status=403)

    # Must be POST request
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

    try:
        data = json.loads(request.body)

        # Validate required fields
        if not data.get('name'):
            return JsonResponse({
                'success': False,
                'message': 'Form name is required'
            }, status=400)

        # Get or create the form template
        template_id = data.get('id')

        with transaction.atomic():
            if template_id:
                # Update existing template
                form_template = get_object_or_404(FormTemplate, id=template_id)

                # Check if user can edit this template
                if form_template.created_by != user and not user.is_superuser:
                    return JsonResponse({
                        'success': False,
                        'message': 'You can only edit your own form templates'
                    }, status=403)

                # Track if form was previously synced to Kobo
                was_synced = form_template.kobo_asset_uid and form_template.kobo_sync_status == 'synced'

                # Check if fields have changed (affects Kobo form)
                new_fields = data.get('fields', [])
                fields_changed = form_template.form_fields != new_fields

                form_template.name = data.get('name')
                form_template.description = data.get('description', '')
                form_template.form_type = data.get('form_type', 'custom_form')
                form_template.status = data.get('status', 'draft')
                form_template.form_purpose = data.get('form_purpose', 'general')
                form_template.field_mapping = data.get('field_mapping', {})
                form_template.sync_to_kobo = data.get('sync_to_kobo', False)
                form_template.allow_multiple_submissions = data.get('allow_multiple_submissions', False)
                form_template.require_photo_evidence = data.get('require_photo_evidence', False)
                form_template.require_gps_location = data.get('require_gps_location', False)

                # Mark as outdated if was synced and fields changed
                if was_synced and fields_changed:
                    form_template.kobo_sync_status = 'sync_outdated'
                    form_template.kobo_version += 1

                form_template.save()

                # Delete existing fields and recreate
                form_template.fields.all().delete()

            else:
                # Create new template
                form_template = FormTemplate.objects.create(
                    name=data.get('name'),
                    description=data.get('description', ''),
                    form_type=data.get('form_type', 'custom_form'),
                    status=data.get('status', 'draft'),
                    form_purpose=data.get('form_purpose', 'general'),
                    field_mapping=data.get('field_mapping', {}),
                    sync_to_kobo=data.get('sync_to_kobo', False),
                    allow_multiple_submissions=data.get('allow_multiple_submissions', False),
                    require_photo_evidence=data.get('require_photo_evidence', False),
                    require_gps_location=data.get('require_gps_location', False),
                    created_by=user
                )

            # Save form fields
            fields_data = data.get('fields', [])
            for order, field_data in enumerate(fields_data):
                validation = field_data.get('validation', {})
                FormField.objects.create(
                    form_template=form_template,
                    field_name=field_data.get('name', f'field_{order}'),
                    field_label=field_data.get('label', 'Untitled Field'),
                    field_type=field_data.get('type', 'text'),
                    required=field_data.get('required', False),
                    help_text=field_data.get('helpText', ''),
                    choices=field_data.get('choices', []),
                    min_value=validation.get('min') if validation.get('min') else None,
                    max_value=validation.get('max') if validation.get('max') else None,
                    order=order
                )

            # Store fields in JSONField as backup
            form_template.form_fields = fields_data
            form_template.save()

            # Handle Field Associate assignments
            fa_ids = data.get('field_associates', [])
            if fa_ids:
                # Get currently assigned FA IDs
                current_fa_ids = set(FormFieldAssociate.objects.filter(
                    form_template=form_template
                ).values_list('field_associate_id', flat=True))

                new_fa_ids = set(int(fa_id) for fa_id in fa_ids if fa_id)

                # Add new FA assignments
                for fa_id in new_fa_ids - current_fa_ids:
                    try:
                        fa_user = User.objects.get(id=fa_id, role='field_associate')
                        FormFieldAssociate.objects.create(
                            form_template=form_template,
                            field_associate=fa_user,
                            assigned_by=user,
                            status='pending'
                        )
                    except User.DoesNotExist:
                        pass

                # Remove FA assignments that are no longer selected
                FormFieldAssociate.objects.filter(
                    form_template=form_template,
                    field_associate_id__in=(current_fa_ids - new_fa_ids)
                ).delete()

        return JsonResponse({
            'success': True,
            'message': 'Form template saved successfully!',
            'id': form_template.id,
            'redirect_url': f'/forms/templates/{form_template.id}/builder/'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error saving form: {str(e)}'
        }, status=500)


@login_required
def form_template_builder(request, pk):
    """Edit existing form template"""
    user = request.user

    form_template = get_object_or_404(FormTemplate, pk=pk)

    # Permission check - allow admin roles, or PM who created the form
    can_edit = (
        user.is_superuser or
        user.role in ['me_staff', 'ict_admin'] or
        (user.role == 'program_manager' and form_template.created_by == user)
    )

    if not can_edit:
        messages.error(request, 'You do not have permission to edit this form')
        return redirect('forms:dashboard')

    # Get form fields
    form_fields = form_template.fields.all().order_by('order')

    # Get available Field Associates for assignment
    field_associates = User.objects.filter(role='field_associate', is_active=True).order_by('first_name', 'last_name')

    # Get currently assigned FAs
    assigned_fa_ids = FormFieldAssociate.objects.filter(
        form_template=form_template
    ).values_list('field_associate_id', flat=True)

    context = {
        'page_title': f'Edit Form: {form_template.name}',
        'form_template': form_template,
        'form_fields': form_fields,
        'field_associates': field_associates,
        'assigned_fa_ids': list(assigned_fa_ids),
        'can_assign_fa': user.role in ['program_manager', 'me_staff', 'ict_admin'] or user.is_superuser,
    }

    return render(request, 'forms/template_builder.html', context)


# ==================== Form Assignment Views ====================

@login_required
def form_assignment_create(request):
    """Create a new form assignment"""
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin', 'field_associate'] and not user.is_superuser:
        messages.error(request, 'You do not have permission to assign forms')
        return redirect('forms:dashboard')

    if request.method == 'POST':
        try:
            form_template_id = request.POST.get('form_template')
            mentor_id = request.POST.get('mentor')
            household_id = request.POST.get('household')
            business_group_id = request.POST.get('business_group')
            due_date = request.POST.get('due_date')

            form_template = get_object_or_404(FormTemplate, id=form_template_id)
            mentor = get_object_or_404(User, id=mentor_id, role='mentor')

            # Create assignment
            assignment = FormAssignment.objects.create(
                form_template=form_template,
                assigned_to=mentor,
                assigned_by=user,
                household_id=household_id if household_id else None,
                business_group_id=business_group_id if business_group_id else None,
                due_date=due_date if due_date else None,
                status='pending'
            )

            messages.success(request, f'Form assigned to {mentor.get_full_name()} successfully!')
            return redirect('forms:assignment_detail', pk=assignment.id)

        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')

    # Get available forms and mentors
    form_templates = FormTemplate.objects.filter(status='active')
    mentors = User.objects.filter(role='mentor', is_active=True)
    households = Household.objects.all()[:100]  # Limit for performance
    business_groups = BusinessGroup.objects.all()[:100]

    context = {
        'page_title': 'Assign Form',
        'form_templates': form_templates,
        'mentors': mentors,
        'households': households,
        'business_groups': business_groups,
    }

    return render(request, 'forms/assignment_create.html', context)


@login_required
def assignment_detail(request, pk):
    """View assignment details"""
    assignment = get_object_or_404(FormAssignment, pk=pk)

    # Permission check
    user = request.user
    if not (user.is_superuser or
            user.role in ['me_staff', 'ict_admin', 'field_associate'] or
            assignment.assigned_to == user):
        messages.error(request, 'You do not have permission to view this assignment')
        return redirect('forms:dashboard')

    context = {
        'page_title': f'Assignment: {assignment.form_template.name}',
        'assignment': assignment,
    }

    return render(request, 'forms/assignment_detail.html', context)


@login_required
def assign_to_mentor(request, assignment_pk):
    """Field associate assigns form to specific mentor"""
    user = request.user

    # Permission check
    if user.role not in ['field_associate', 'me_staff', 'ict_admin'] and not user.is_superuser:
        messages.error(request, 'You do not have permission to assign to mentors')
        return redirect('forms:dashboard')

    assignment = get_object_or_404(FormAssignment, pk=assignment_pk)

    if request.method == 'POST':
        mentor_id = request.POST.get('mentor_id')
        mentor = get_object_or_404(User, id=mentor_id, role='mentor')

        # Create mentor assignment
        mentor_assignment = FormAssignmentMentor.objects.create(
            form_assignment=assignment,
            mentor=mentor,
            assigned_by_fa=user,
            status='pending'
        )

        messages.success(request, f'Form assigned to {mentor.get_full_name()}')
        return redirect('forms:assignment_detail', pk=assignment.pk)

    mentors = User.objects.filter(role='mentor', is_active=True)

    context = {
        'assignment': assignment,
        'mentors': mentors,
    }

    return render(request, 'forms/assign_to_mentor.html', context)


@login_required
def fill_form(request, assignment_pk):
    """Mentor fills out assigned form"""
    user = request.user

    assignment = get_object_or_404(FormAssignment, pk=assignment_pk)

    # Permission check
    if assignment.assigned_to != user and not user.is_superuser:
        messages.error(request, 'This form is not assigned to you')
        return redirect('forms:my_assignments')

    if request.method == 'POST':
        try:
            # Get form data from POST
            form_data = {}
            gps_latitude = None
            gps_longitude = None

            for field in assignment.form_template.fields.all():
                field_name = f'field_{field.id}'

                # Handle different field types
                if field.field_type == 'location':
                    # GPS location has separate lat/lng fields
                    lat = request.POST.get(f'{field_name}_lat')
                    lng = request.POST.get(f'{field_name}_lng')
                    if lat and lng:
                        form_data[field.field_name] = f"{lat} {lng}"
                        # Also store in submission-level GPS fields
                        try:
                            gps_latitude = float(lat)
                            gps_longitude = float(lng)
                        except (ValueError, TypeError):
                            pass

                elif field.field_type == 'checkbox':
                    # Checkboxes can have multiple values
                    values = request.POST.getlist(field_name)
                    if values:
                        form_data[field.field_name] = values if len(values) > 1 else values[0]

                elif field.field_type in ['file', 'image', 'audio', 'video']:
                    # Handle file uploads
                    if field_name in request.FILES:
                        uploaded_file = request.FILES[field_name]
                        # Store file path reference (actual file handling would need additional logic)
                        form_data[field.field_name] = f"uploaded:{uploaded_file.name}"

                elif field.field_type == 'signature':
                    # Signature is stored as base64 data URL
                    sig_data = request.POST.get(field_name)
                    if sig_data and sig_data.startswith('data:image'):
                        form_data[field.field_name] = sig_data

                elif field.field_type in ['section', 'group', 'note']:
                    # Skip organizational/display-only fields
                    continue

                else:
                    # Standard field types
                    if field_name in request.POST:
                        value = request.POST.get(field_name)
                        if value:  # Only store non-empty values
                            form_data[field.field_name] = value

            # Create submission
            submission = FormSubmission.objects.create(
                form_template=assignment.form_template,
                form_assignment=assignment,
                submitted_by=user,
                household=assignment.household,
                business_group=assignment.business_group,
                form_data=form_data,
                data_source='web_form',
                gps_latitude=gps_latitude,
                gps_longitude=gps_longitude
            )

            # Handle photo evidence if required
            if assignment.form_template.require_photo_evidence and 'photo_evidence' in request.FILES:
                submission.photo_evidence = request.FILES['photo_evidence']
                submission.save()

            # Update assignment status
            assignment.status = 'completed'
            assignment.save()

            messages.success(request, 'Form submitted successfully!')
            return redirect('forms:submission_detail', pk=submission.id)

        except Exception as e:
            messages.error(request, f'Error submitting form: {str(e)}')

    # Get form fields with options properly formatted
    form_fields = assignment.form_template.fields.all().order_by('order')

    # Add options property for select/radio/checkbox fields
    for field in form_fields:
        if field.field_type in ['select', 'radio', 'checkbox'] and field.choices:
            # Ensure choices are in the right format
            if isinstance(field.choices, list):
                field.options = field.choices
            else:
                field.options = []

    context = {
        'page_title': f'Fill Form: {assignment.form_template.name}',
        'assignment': assignment,
        'form_fields': form_fields,
    }

    return render(request, 'forms/fill_form.html', context)


@login_required
def submission_detail(request, pk):
    """View submission details"""
    submission = get_object_or_404(FormSubmission, pk=pk)

    # Permission check
    user = request.user
    if not (user.is_superuser or
            user.role in ['me_staff', 'ict_admin'] or
            submission.submitted_by == user):
        messages.error(request, 'You do not have permission to view this submission')
        return redirect('forms:dashboard')

    # Build field label lookup from FormField definitions
    field_labels = {}
    field_types = {}
    for field in submission.form_template.fields.all():
        field_labels[field.field_name] = field.field_label
        field_types[field.field_name] = field.field_type

    # Meta field prefixes to filter out
    meta_prefixes = ('_', 'meta/', 'formhub/', '__version__', 'deviceid', 'instanceID')

    # Filter and format form data
    filtered_data = []
    if submission.form_data:
        for key, value in submission.form_data.items():
            # Skip meta fields
            if key.startswith(meta_prefixes) or key in ['meta', 'formhub']:
                continue
            # Skip empty values
            if value is None or value == '':
                continue

            # Get human-readable label
            label = field_labels.get(key, key.replace('_', ' ').title())
            field_type = field_types.get(key, 'text')

            filtered_data.append({
                'key': key,
                'label': label,
                'value': value,
                'type': field_type,
            })

    context = {
        'page_title': f'Submission: {submission.form_template.name}',
        'submission': submission,
        'filtered_data': filtered_data,
    }

    return render(request, 'forms/submission_detail.html', context)


@login_required
def my_assignments(request):
    """Mentor views their assigned forms"""
    user = request.user

    if user.role != 'mentor':
        messages.error(request, 'This page is for mentors only')
        return redirect('forms:dashboard')

    # Get direct assignments (where mentor is directly assigned)
    assignments = FormAssignment.objects.filter(
        mentor=user
    ).select_related('form_template', 'assigned_by').order_by('-assigned_at')

    # Get mentor assignments from field associates
    mentor_assignments = FormAssignmentMentor.objects.filter(
        mentor=user
    ).select_related('assignment__form_template', 'assigned_by_fa').order_by('-assigned_at')

    context = {
        'page_title': 'My Assigned Forms',
        'assignments': assignments,
        'mentor_assignments': mentor_assignments,
    }

    return render(request, 'forms/my_assignments.html', context)


# ==================== Submissions Views ====================

@login_required
def form_submissions_list(request, form_template_id):
    """
    List all submissions for a specific form template.
    Shows both web submissions and KoboToolbox synced submissions.
    """
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin'] and not user.is_superuser:
        messages.error(request, 'You do not have permission to view submissions')
        return redirect('forms:dashboard')

    form_template = get_object_or_404(FormTemplate, id=form_template_id)

    # Get all submissions for this form
    submissions = FormSubmission.objects.filter(
        form_template=form_template
    ).select_related('submitted_by', 'household', 'business_group').order_by('-submission_date')

    # Filter by data source
    source_filter = request.GET.get('source')
    if source_filter in ['web_form', 'kobo_sync', 'kobo_webhook']:
        submissions = submissions.filter(data_source=source_filter)

    # Statistics
    total_count = submissions.count()
    web_count = submissions.filter(data_source='web_form').count()
    kobo_count = submissions.filter(data_source__in=['kobo_sync', 'kobo_webhook']).count()

    # Build chart data for select/radio/checkbox fields
    chart_fields = []
    choice_fields = form_template.fields.filter(
        field_type__in=['radio', 'select', 'checkbox']
    ).order_by('order')[:6]  # Limit to 6 charts for performance

    all_submissions_data = list(submissions.values_list('form_data', flat=True))

    for field in choice_fields:
        # Count responses for this field
        response_counts = {}
        for form_data in all_submissions_data:
            if form_data and field.field_name in form_data:
                value = form_data[field.field_name]
                if value:
                    # Handle multiple values (checkbox)
                    if isinstance(value, list):
                        for v in value:
                            response_counts[v] = response_counts.get(v, 0) + 1
                    else:
                        response_counts[value] = response_counts.get(value, 0) + 1

        if response_counts:
            # Sort by count descending, take top 8
            sorted_responses = sorted(response_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            labels = [item[0] for item in sorted_responses]
            values = [item[1] for item in sorted_responses]

            # Create label lookup from field choices
            choice_labels = {}
            if field.choices:
                for choice in field.choices:
                    choice_labels[choice.get('value', '')] = choice.get('label', choice.get('value', ''))

            # Map values to display labels
            display_labels = [choice_labels.get(lbl, lbl) for lbl in labels]

            chart_fields.append({
                'field_name': field.field_name,
                'field_label': field.field_label,
                'field_type': field.field_type,
                'labels': display_labels,
                'values': values,
                'total_responses': sum(values),
            })

    # Submissions by date (for timeline chart)
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    submissions_by_date = submissions.annotate(
        date=TruncDate('submission_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:30]  # Last 30 days with data

    timeline_data = {
        'labels': [item['date'].strftime('%b %d') if item['date'] else '' for item in submissions_by_date],
        'values': [item['count'] for item in submissions_by_date],
    }

    # Pagination
    paginator = Paginator(submissions, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': f'Submissions: {form_template.name}',
        'form_template': form_template,
        'submissions': page_obj,
        'page_obj': page_obj,
        'total_count': total_count,
        'web_count': web_count,
        'kobo_count': kobo_count,
        'source_filter': source_filter,
        'chart_fields': chart_fields,
        'timeline_data': timeline_data,
    }

    return render(request, 'forms/submissions_list.html', context)


@login_required
def fetch_submissions_from_kobo(request, form_template_id):
    """
    Manually fetch submissions from KoboToolbox.
    Use this when webhooks aren't available (e.g., localhost development).
    """
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin'] and not user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to fetch submissions'
        }, status=403)

    # Must be POST request
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

    form_template = get_object_or_404(FormTemplate, id=form_template_id)

    # Check if form is synced to Kobo
    if not form_template.kobo_asset_uid:
        return JsonResponse({
            'success': False,
            'message': 'This form is not synced to KoboToolbox yet'
        }, status=400)

    # Import and call the fetch function
    from .kobo_service import fetch_kobo_submissions

    try:
        success, message, count = fetch_kobo_submissions(form_template, user=user)

        return JsonResponse({
            'success': success,
            'message': message,
            'new_submissions': count,
            'redirect_url': f'/forms/templates/{form_template_id}/submissions/'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching submissions: {str(e)}'
        }, status=500)


@login_required
def check_beneficiary_lookup_api(request, form_template_id):
    """
    API endpoint to check if a form will have beneficiary lookup enabled.
    Used by form builder to show indicator before syncing.
    """
    try:
        form_template = get_object_or_404(FormTemplate, id=form_template_id)

        from .kobo_service import check_form_has_beneficiary_lookup
        result = check_form_has_beneficiary_lookup(form_template)

        return JsonResponse({
            'success': True,
            'beneficiary_lookup': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def forms_stats_api(request):
    """
    API endpoint to get forms statistics for Kobo settings dashboard.
    Returns count of synced forms and Kobo submissions.
    """
    try:
        # Count forms synced to Kobo
        synced_forms = FormTemplate.objects.filter(
            kobo_asset_uid__isnull=False
        ).exclude(kobo_asset_uid='').count()

        # Count submissions from Kobo
        kobo_submissions = FormSubmission.objects.filter(
            data_source__in=['kobo_sync', 'kobo_webhook']
        ).count()

        # Count total forms and submissions
        total_forms = FormTemplate.objects.count()
        total_submissions = FormSubmission.objects.count()

        return JsonResponse({
            'synced_forms': synced_forms,
            'kobo_submissions': kobo_submissions,
            'total_forms': total_forms,
            'total_submissions': total_submissions,
        })
    except Exception as e:
        return JsonResponse({
            'synced_forms': 0,
            'kobo_submissions': 0,
            'error': str(e)
        })


@login_required
def copy_form_template(request, pk):
    """
    Create a copy of an existing form template with all its fields.
    """
    user = request.user

    # Permission check
    if user.role not in ['me_staff', 'ict_admin'] and not user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'You do not have permission to copy forms'
        }, status=403)

    # Must be POST request
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

    # Get original template
    original = get_object_or_404(FormTemplate, pk=pk)

    try:
        with transaction.atomic():
            # Create copy of the template
            new_template = FormTemplate.objects.create(
                name=f"{original.name} (Copy)",
                description=original.description,
                form_type=original.form_type,
                status='draft',  # Always start as draft
                sync_to_kobo=False,  # Don't auto-sync copies
                allow_multiple_submissions=original.allow_multiple_submissions,
                require_photo_evidence=original.require_photo_evidence,
                require_gps_location=original.require_gps_location,
                form_fields=original.form_fields,  # Copy JSON backup
                created_by=user
            )

            # Copy all fields
            for field in original.fields.all().order_by('order'):
                FormField.objects.create(
                    form_template=new_template,
                    field_name=field.field_name,
                    field_label=field.field_label,
                    field_type=field.field_type,
                    required=field.required,
                    help_text=field.help_text,
                    placeholder=field.placeholder,
                    default_value=field.default_value,
                    choices=field.choices,
                    min_value=field.min_value,
                    max_value=field.max_value,
                    min_length=field.min_length,
                    max_length=field.max_length,
                    validation_regex=field.validation_regex,
                    show_if_field=field.show_if_field,
                    show_if_value=field.show_if_value,
                    order=field.order
                )

            return JsonResponse({
                'success': True,
                'message': f'Form copied successfully as "{new_template.name}"',
                'new_id': new_template.id,
                'redirect_url': f'/forms/templates/{new_template.id}/builder/'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error copying form: {str(e)}'
        }, status=500)


@login_required
def form_assign_mentors(request, form_template_id):
    """FA assigns mentors to a form they're assigned to"""
    user = request.user
    form_template = get_object_or_404(FormTemplate, id=form_template_id)

    # Check if user is FA assigned to this form
    try:
        fa_assignment = FormFieldAssociate.objects.get(
            form_template=form_template,
            field_associate=user
        )
    except FormFieldAssociate.DoesNotExist:
        # Allow admin roles to also manage mentor assignments
        if not (user.is_superuser or user.role in ['me_staff', 'ict_admin', 'program_manager']):
            messages.error(request, 'You are not assigned to manage this form')
            return redirect('forms:dashboard')
        fa_assignment = None

    if request.method == 'POST':
        mentor_ids = request.POST.getlist('mentors[]') or request.POST.getlist('mentors')

        if fa_assignment:
            # Get current mentor assignments for this FA
            current_mentor_ids = set(FormMentorAssignment.objects.filter(
                form_fa=fa_assignment
            ).values_list('mentor_id', flat=True))

            new_mentor_ids = set(int(m_id) for m_id in mentor_ids if m_id)

            # Add new mentor assignments
            added_count = 0
            for mentor_id in new_mentor_ids - current_mentor_ids:
                try:
                    mentor = User.objects.get(id=mentor_id, role='mentor')
                    FormMentorAssignment.objects.create(
                        form_fa=fa_assignment,
                        mentor=mentor,
                        assigned_by=user
                    )
                    added_count += 1
                except User.DoesNotExist:
                    pass

            # Remove mentor assignments that are no longer selected
            removed_count = FormMentorAssignment.objects.filter(
                form_fa=fa_assignment,
                mentor_id__in=(current_mentor_ids - new_mentor_ids)
            ).delete()[0]

            messages.success(request, f'Mentor assignments updated. Added: {added_count}, Removed: {removed_count}')
        else:
            # Admin is managing - get or create FA assignment for admin management
            messages.info(request, 'Admin mentor assignment not yet implemented for non-FA users')

        return redirect('forms:form_assign_mentors', form_template_id=form_template_id)

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
        assigned_mentor_ids = list(FormMentorAssignment.objects.filter(
            form_fa=fa_assignment
        ).values_list('mentor_id', flat=True))

    context = {
        'page_title': f'Assign Mentors - {form_template.name}',
        'form_template': form_template,
        'fa_assignment': fa_assignment,
        'available_mentors': available_mentors,
        'assigned_mentor_ids': assigned_mentor_ids,
    }

    return render(request, 'forms/form_assign_mentors.html', context)


@login_required
def form_fa_assignments_list(request):
    """List all forms assigned to the current FA with their mentor assignments"""
    user = request.user

    if user.role != 'field_associate':
        messages.error(request, 'This page is for Field Associates only')
        return redirect('forms:dashboard')

    # Get forms assigned to this FA
    fa_assignments = FormFieldAssociate.objects.filter(
        field_associate=user
    ).select_related('form_template', 'assigned_by').order_by('-assigned_at')

    context = {
        'page_title': 'My Form Assignments',
        'fa_assignments': fa_assignments,
    }

    return render(request, 'forms/fa_assignments_list.html', context)
