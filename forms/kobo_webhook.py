"""
KoboToolbox Webhook Handler
Receives and processes form submissions from KoboToolbox
"""

import json
import re
import hmac
import hashlib
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from .models import (
    FormTemplate,
    FormSubmission,
    FormAssignment,
    KoboWebhookLog,
)

logger = logging.getLogger(__name__)


def verify_kobo_signature(request):
    """
    Verify the webhook signature from KoboToolbox.

    Returns:
        bool: True if signature is valid or no secret is configured, False otherwise
    """
    webhook_secret = getattr(settings, 'KOBO_WEBHOOK_SECRET', '')

    # If no secret configured, skip validation (development mode)
    if not webhook_secret:
        return True

    # Get signature from headers (KoboToolbox uses X-Kobo-Hook-Signature)
    signature = request.headers.get('X-Kobo-Hook-Signature', '')
    if not signature:
        # Also check alternative header names
        signature = request.headers.get('X-Hook-Signature', '')

    if not signature:
        logger.warning("Webhook received without signature header")
        return False

    # Calculate expected signature
    try:
        expected = hmac.new(
            webhook_secret.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures (timing-safe comparison)
        # Handle both plain hex and prefixed formats
        if signature.startswith('sha256='):
            signature = signature[7:]

        return hmac.compare_digest(signature.lower(), expected.lower())
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False


@csrf_exempt
@require_POST
def kobo_webhook_receiver(request):
    """
    Webhook endpoint for KoboToolbox submissions
    URL: /forms/kobo/webhook/

    Receives submissions and queues them for processing.
    Validates webhook signature if KOBO_WEBHOOK_SECRET is configured.

    Returns:
        JsonResponse: 200 OK with status message
    """
    try:
        # Security: Verify webhook signature if secret is configured
        if not verify_kobo_signature(request):
            logger.warning(f"Invalid webhook signature from {get_client_ip(request)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid webhook signature'
            }, status=403)

        # Get client IP and user agent
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # Parse JSON payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        # Extract submission UUID and asset UID
        submission_uuid = payload.get('_uuid')
        asset_uid = payload.get('formhub/uuid') or payload.get('_xform_id_string')

        if not submission_uuid:
            return JsonResponse({'status': 'error', 'message': 'Missing submission UUID'}, status=400)

        # Check for duplicate
        if KoboWebhookLog.objects.filter(submission_uuid=submission_uuid).exists():
            return JsonResponse({
                'status': 'duplicate',
                'message': 'Submission already processed'
            }, status=200)

        # Create webhook log
        webhook_log = KoboWebhookLog.objects.create(
            kobo_asset_uid=asset_uid or '',
            submission_uuid=submission_uuid,
            raw_payload=payload,
            status='received',
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Process submission immediately (or queue for async processing)
        # For now, process synchronously
        try:
            processor = KoboSubmissionProcessor()
            processor.process_submission(webhook_log.id)
        except Exception as e:
            # Log error but still return 200 to prevent Kobo from retrying
            webhook_log.status = 'failed'
            webhook_log.error_message = str(e)
            webhook_log.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Submission received and processed',
            'webhook_log_id': webhook_log.id
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


class KoboSubmissionProcessor:
    """
    Process submissions received from Kobo webhook
    Maps Kobo submission data to UPG FormSubmission
    """

    def process_submission(self, webhook_log_id):
        """
        Main processing function

        Args:
            webhook_log_id: ID of KoboWebhookLog to process

        Returns:
            FormSubmission: Created submission instance
        """
        webhook_log = KoboWebhookLog.objects.get(id=webhook_log_id)

        try:
            with transaction.atomic():
                payload = webhook_log.raw_payload

                # Find matching FormTemplate by kobo_asset_uid
                kobo_asset_uid = webhook_log.kobo_asset_uid
                form_template = FormTemplate.objects.filter(
                    kobo_asset_uid=kobo_asset_uid
                ).first()

                if not form_template:
                    raise ValueError(f"No FormTemplate found for asset UID: {kobo_asset_uid}")

                webhook_log.form_template = form_template

                # Extract submission metadata
                submission_time = parse_datetime(payload.get('_submission_time'))
                submitted_by_username = payload.get('_submitted_by') or payload.get('username')

                # Find user (mentor/field associate)
                from django.contrib.auth import get_user_model
                User = get_user_model()

                submitted_by = None
                if submitted_by_username:
                    submitted_by = User.objects.filter(username=submitted_by_username).first()

                # If no user found, try to get from active assignment
                if not submitted_by:
                    # Get any active assignment for this form
                    assignment = FormAssignment.objects.filter(
                        form_template=form_template,
                        status__in=['pending', 'accepted', 'in_progress']
                    ).first()

                    if assignment:
                        submitted_by = assignment.mentor or assignment.field_associate

                # Fall back to form creator if still no user found
                if not submitted_by:
                    submitted_by = form_template.created_by

                # Find assignment (if applicable)
                assignment = FormAssignment.objects.filter(
                    form_template=form_template,
                    status__in=['pending', 'accepted', 'in_progress', 'completed']
                ).first()

                # Map Kobo data to UPG form_data
                form_data = self.map_kobo_data_to_upg(payload, form_template)

                # Extract related entities
                household, business_group = self.extract_related_entities(form_data)

                # Extract GPS location
                gps_latitude, gps_longitude, location_name = self.extract_gps_data(payload)

                # MIS Validation and Household Creation
                validation_status = 'not_validated'
                validation_message = ''

                # Import validation functions
                from .beneficiary_lookup import (
                    validate_submission_for_purpose,
                    process_new_registration,
                    update_household_from_submission
                )

                # Process based on form purpose
                if form_template.form_purpose == 'new_registration':
                    # Try to create new household
                    result = process_new_registration(
                        form_template=form_template,
                        form_data=form_data,
                        gps_latitude=gps_latitude,
                        gps_longitude=gps_longitude,
                        created_by=submitted_by
                    )

                    if result['status'] == 'created':
                        household = result['household']
                        validation_status = 'data_created'
                        validation_message = result['message']
                    elif result['status'] == 'duplicate':
                        household = result['household']
                        validation_status = 'duplicate_detected'
                        validation_message = result['message']
                    else:
                        validation_status = 'validation_failed'
                        validation_message = result['message']

                elif form_template.form_purpose in ['program_enrollment', 'survey', 'update_details']:
                    # Validate and link to existing household
                    validation = validate_submission_for_purpose(form_template, form_data)
                    validation_status = validation['status']
                    validation_message = validation['message']

                    if validation['household']:
                        household = validation['household']

                        # Update household if form_purpose is update_details
                        if form_template.form_purpose == 'update_details' and validation['should_update']:
                            success, updated_fields, update_msg = update_household_from_submission(
                                household=household,
                                form_data=form_data,
                                field_mapping=form_template.field_mapping
                            )
                            if success and updated_fields:
                                validation_status = 'data_updated'
                                validation_message = f'{validation_message}. {update_msg}'

                # Create FormSubmission
                submission = FormSubmission.objects.create(
                    assignment=assignment,
                    form_template=form_template,
                    submitted_by=submitted_by,
                    submission_date=submission_time or timezone.now(),
                    form_data=form_data,
                    gps_latitude=gps_latitude,
                    gps_longitude=gps_longitude,
                    location_name=location_name,
                    status='submitted',
                    household=household,
                    business_group=business_group,
                    kobo_submission_uuid=webhook_log.submission_uuid,
                    kobo_submission_time=submission_time,
                    data_source='kobo_webhook',
                    validation_status=validation_status,
                    validation_message=validation_message,
                    matched_household=household,
                )

                # Update webhook log
                webhook_log.status = 'processed'
                webhook_log.processed_at = timezone.now()
                webhook_log.form_submission = submission
                webhook_log.processed_data = {
                    'submission_id': submission.id,
                    'household_id': household.id if household else None,
                    'business_group_id': business_group.id if business_group else None,
                }
                webhook_log.save()

                return submission

        except Exception as e:
            # Update webhook log with error
            webhook_log.status = 'failed'
            webhook_log.error_message = str(e)
            webhook_log.processed_at = timezone.now()
            webhook_log.save()

            raise

    def map_kobo_data_to_upg(self, kobo_data, form_template):
        """
        Map Kobo submission fields to UPG form_data structure

        Args:
            kobo_data: Raw Kobo submission payload
            form_template: FormTemplate instance

        Returns:
            dict: Mapped form_data
        """
        form_data = {}

        # Get all fields from form template
        for field in form_template.fields.all():
            field_name = field.field_name

            # Get value from Kobo data
            value = kobo_data.get(field_name)

            if value is not None:
                # Clean and validate value
                if field.field_type == 'phone':
                    value = self.clean_phone_number(value)
                elif field.field_type == 'number':
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        value = None
                elif field.field_type == 'boolean':
                    value = value in ['yes', 'true', '1', True]

                form_data[field_name] = value

        # Also include any extra fields from Kobo that aren't in form template
        # This helps preserve all submission data
        for key, value in kobo_data.items():
            if not key.startswith('_') and key not in form_data:
                form_data[key] = value

        return form_data

    def extract_related_entities(self, form_data):
        """
        Extract and link to related entities (household, business_group)

        Args:
            form_data: Mapped form data

        Returns:
            tuple: (household, business_group) or (None, None)
        """
        household = None
        business_group = None

        # Try to find household by ID
        household_id = form_data.get('household_id')
        if household_id:
            from households.models import Household
            try:
                household = Household.objects.get(id=household_id)
            except Household.DoesNotExist:
                # Check settings if we should create new household
                allow_new = getattr(settings, 'KOBO_ALLOW_NEW_HOUSEHOLDS', True)
                if allow_new:
                    # Could create new household here based on form data
                    # For now, just leave as None
                    pass

        # Try to find business group by ID
        bg_id = form_data.get('business_group_id')
        if bg_id:
            from business_groups.models import BusinessGroup
            try:
                business_group = BusinessGroup.objects.get(id=bg_id)
            except BusinessGroup.DoesNotExist:
                pass

        return household, business_group

    def extract_gps_data(self, kobo_data):
        """
        Extract GPS location data from Kobo submission

        Args:
            kobo_data: Raw Kobo submission payload

        Returns:
            tuple: (latitude, longitude, location_name)
        """
        latitude = None
        longitude = None
        location_name = ''

        # Look for geopoint field (can be named 'location', 'gps', 'household_gps', etc.)
        gps_field = None
        for key in ['household_gps', 'gps_location', 'location', 'geopoint']:
            if key in kobo_data:
                gps_field = kobo_data[key]
                break

        if gps_field:
            # Kobo geopoint format: "latitude longitude altitude accuracy"
            parts = str(gps_field).split()
            if len(parts) >= 2:
                try:
                    latitude = float(parts[0])
                    longitude = float(parts[1])
                except (ValueError, IndexError):
                    pass

        # Location name
        location_name = kobo_data.get('location_name', '')

        return latitude, longitude, location_name

    def clean_phone_number(self, phone):
        """
        Clean and validate Kenya phone number

        Args:
            phone: Phone number string

        Returns:
            str: Cleaned phone number or original if invalid
        """
        if not phone:
            return ''

        # Remove non-numeric characters
        phone = re.sub(r'\D', '', str(phone))

        # Kenya formats: 07XXXXXXXX or 01XXXXXXXX
        if re.match(r'^(07|01)\d{8}$', phone):
            return phone

        # International format: +254... -> 0...
        if phone.startswith('254') and len(phone) == 12:
            return f"0{phone[3:]}"

        # Return original if no match
        return phone


def parse_datetime(dt_string):
    """
    Parse datetime string from Kobo submission

    Args:
        dt_string: Datetime string from Kobo

    Returns:
        datetime: Parsed datetime object or None
    """
    if not dt_string:
        return None

    try:
        # Kobo format: "2024-01-15T10:30:00.000Z"
        # Try ISO format first
        if 'T' in dt_string:
            dt_string = dt_string.replace('Z', '+00:00')
            return datetime.fromisoformat(dt_string)

        # Try other formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
            try:
                return datetime.strptime(dt_string, fmt)
            except ValueError:
                continue

        return None
    except Exception:
        return None


def get_client_ip(request):
    """
    Get client IP address from request

    Args:
        request: Django request object

    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
