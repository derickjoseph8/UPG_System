"""
KoboToolbox Integration Service
Handles bi-directional sync between UPG FormTemplates and KoboToolbox forms
"""

import requests
import json
import time
from datetime import datetime, timezone
from django.conf import settings
from django.utils import timezone as django_timezone
from django.db import transaction
from .models import FormTemplate, KoboSyncLog
from core.kobo_export import (
    export_households_csv,
    export_villages_csv,
    export_business_groups_csv,
    export_mentors_csv,
)


def get_kobo_settings_from_db():
    """
    Get KoboToolbox settings from database (SystemConfiguration model).
    Falls back to Django settings if database is not available.
    """
    try:
        from settings_module.models import SystemConfiguration

        def get_config(key, default=''):
            try:
                config = SystemConfiguration.objects.get(key=key)
                return config.value
            except SystemConfiguration.DoesNotExist:
                return default

        api_url = get_config('kobo_api_url', 'https://kf.kobotoolbox.org/api/v2')
        api_token = get_config('kobo_api_token', '')

        return {
            'api_url': api_url,
            'token': api_token,
            'base_url': api_url.replace('/api/v2', ''),  # Derive base URL from API URL
            'enabled': True,
        }
    except Exception as e:
        # Fallback to Django settings if database not ready
        return {
            'api_url': getattr(settings, 'KOBO_API_URL', 'https://kf.kobotoolbox.org/api/v2'),
            'token': getattr(settings, 'KOBO_API_TOKEN', ''),
            'base_url': getattr(settings, 'KOBO_BASE_URL', 'https://kf.kobotoolbox.org'),
            'enabled': True,
        }


class KoboAPIClient:
    """
    Client for KoboToolbox API v2
    Handles authentication, requests, and error handling
    """

    def __init__(self):
        # Get settings from database (frontend-configurable)
        kobo_settings = get_kobo_settings_from_db()

        self.api_url = kobo_settings['api_url']
        self.token = kobo_settings['token']
        self.base_url = kobo_settings['base_url']

        if not self.token:
            raise ValueError(
                "KoboToolbox API token not configured. "
                "Please go to Settings > KoboToolbox Settings to add your API token."
            )

        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
        }

    def create_asset(self, name, content, asset_type='survey'):
        """
        Create new form asset in KoboToolbox

        Args:
            name: Form name
            content: XLSForm JSON structure
            asset_type: Asset type (default: 'survey')

        Returns:
            dict: API response with asset details including 'uid'
        """
        url = f"{self.api_url}/assets/"

        payload = {
            'name': name,
            'asset_type': asset_type,
            'content': content,
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()

    def update_asset(self, asset_uid, content=None, name=None):
        """
        Update existing form asset

        Args:
            asset_uid: KoboToolbox asset UID
            content: Updated XLSForm JSON structure (optional)
            name: Updated form name (optional)

        Returns:
            dict: API response
        """
        url = f"{self.api_url}/assets/{asset_uid}/"

        payload = {}
        if content:
            payload['content'] = content
        if name:
            payload['name'] = name

        response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()

    def deploy_asset(self, asset_uid):
        """
        Deploy form to make it available for data collection.
        Uses POST for new deployment, PATCH for re-deployment.

        Args:
            asset_uid: KoboToolbox asset UID

        Returns:
            dict: Deployment response
        """
        url = f"{self.api_url}/assets/{asset_uid}/deployment/"

        payload = {
            'active': True,
        }

        # First try POST (new deployment)
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)

        # If 405 (Method Not Allowed), asset is already deployed - use PATCH instead
        if response.status_code == 405:
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)

        response.raise_for_status()

        return response.json()

    def find_asset_by_name(self, name):
        """
        Find an existing asset by name to avoid duplicates.

        Args:
            name: Form name to search for

        Returns:
            str: Asset UID if found, None otherwise
        """
        url = f"{self.api_url}/assets/"
        params = {'q': f'name:"{name}"'}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            for asset in results:
                if asset.get('name') == name:
                    return asset.get('uid')
            return None
        except Exception:
            return None

    def get_asset(self, asset_uid):
        """
        Retrieve asset details

        Args:
            asset_uid: KoboToolbox asset UID

        Returns:
            dict: Asset details
        """
        url = f"{self.api_url}/assets/{asset_uid}/"

        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        return response.json()

    def delete_asset(self, asset_uid):
        """
        Archive/delete asset

        Args:
            asset_uid: KoboToolbox asset UID

        Returns:
            bool: True if successful
        """
        url = f"{self.api_url}/assets/{asset_uid}/"

        response = requests.delete(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        return True

    def upload_media_file(self, asset_uid, filename, file_content):
        """
        Upload CSV/media files to asset for pulldata() function

        Args:
            asset_uid: KoboToolbox asset UID
            filename: Name of the file (e.g., 'households.csv')
            file_content: File content as string or bytes

        Returns:
            dict: Upload response
        """
        url = f"{self.api_url}/assets/{asset_uid}/files/"

        # Prepare multipart form data
        files = {
            'file': (filename, file_content, 'text/csv'),
        }

        # Remove Content-Type header for multipart upload
        headers = {
            'Authorization': f'Token {self.token}',
        }

        response = requests.post(url, headers=headers, files=files, timeout=60)
        response.raise_for_status()

        return response.json()

    def configure_webhook(self, asset_uid, webhook_url):
        """
        Set up webhook for submission notifications

        Args:
            asset_uid: KoboToolbox asset UID
            webhook_url: URL to receive webhook notifications

        Returns:
            dict: Webhook configuration response
        """
        url = f"{self.api_url}/assets/{asset_uid}/hooks/"

        payload = {
            'name': f'UPG MIS Webhook',
            'endpoint': webhook_url,
            'active': True,
            'subset_fields': [],  # Send all fields
            'email_notification': True,
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()


class XLSFormConverter:
    """
    Convert UPG FormTemplate to XLSForm JSON format
    """

    # Field type mapping from UPG to XLSForm
    FIELD_TYPE_MAP = {
        # Text Fields
        'text': 'text',
        'textarea': 'text',
        'note': 'note',

        # Numeric Fields
        'number': 'integer',
        'decimal': 'decimal',
        'calculate': 'calculate',

        # Contact Fields
        'email': 'text',
        'phone': 'text',

        # Date/Time Fields
        'date': 'date',
        'time': 'time',
        'datetime': 'datetime',

        # Choice Fields
        'select': 'select_one',
        'radio': 'select_one',
        'checkbox': 'select_multiple',
        'boolean': 'select_one yes_no',

        # Media Fields
        'file': 'file',
        'image': 'image',
        'audio': 'audio',
        'video': 'video',

        # Special Fields
        'rating': 'integer',
        'location': 'geopoint',
        'signature': 'image',
        'barcode': 'barcode',
        'range': 'range',

        # Organizational
        'section': 'begin_group',
        'group': 'begin_group',
    }

    def __init__(self, form_template):
        self.form_template = form_template

    def convert_to_xlsform(self):
        """
        Convert FormTemplate to XLSForm JSON

        Returns:
            dict: XLSForm structure with 'survey', 'choices', 'settings'
        """
        xlsform = {
            'survey': [],
            'choices': [],
            'settings': {
                'form_title': self.form_template.name,
                'form_id': f'upg_form_{self.form_template.id}',
                'version': str(self.form_template.kobo_version),
            }
        }

        # Add metadata fields
        self._add_metadata_fields(xlsform['survey'])

        # Check if form needs beneficiary lookup (based on purpose OR mandatory identifier fields)
        needs_lookup = self._check_needs_beneficiary_lookup()
        if needs_lookup:
            self._add_beneficiary_lookup_fields(xlsform)

        # Add form fields
        for field in self.form_template.fields.all().order_by('order'):
            self._add_field_to_survey(field, xlsform)

        return xlsform

    def _check_needs_beneficiary_lookup(self):
        """
        Check if form needs beneficiary lookup functionality.

        Returns True if:
        1. Form purpose is program_enrollment, survey, or update_details, OR
        2. Form has mandatory fields for phone number, ID number, or village
        """
        # Check form purpose
        if self.form_template.form_purpose in ['program_enrollment', 'survey', 'update_details']:
            return True

        # Field name patterns that indicate beneficiary identifier fields
        id_patterns = [
            'id_number', 'national_id', 'id_no', 'idnumber', 'nationalid',
            'head_id_number', 'identification', 'id'
        ]
        phone_patterns = [
            'phone', 'phone_number', 'phonenumber', 'mobile', 'telephone',
            'head_phone', 'contact_phone', 'tel'
        ]
        village_patterns = [
            'village', 'village_name', 'villagename', 'village_id'
        ]

        # Check all form fields for mandatory identifier fields
        for field in self.form_template.fields.all():
            if not field.required:
                continue  # Only check mandatory fields

            field_name_lower = field.field_name.lower()
            field_label_lower = field.field_label.lower() if field.field_label else ''

            # Check for ID number field
            for pattern in id_patterns:
                if pattern in field_name_lower or pattern in field_label_lower:
                    return True

            # Check for phone field
            for pattern in phone_patterns:
                if pattern in field_name_lower or pattern in field_label_lower:
                    return True

            # Check for village field
            for pattern in village_patterns:
                if pattern in field_name_lower or pattern in field_label_lower:
                    return True

            # Also check field type - phone type fields
            if field.field_type == 'phone' and field.required:
                return True

        return False

    def _add_beneficiary_lookup_fields(self, xlsform):
        """
        Add automatic beneficiary lookup fields using pulldata().
        This enables searching for existing beneficiaries and pre-filling their data.

        When user enters ID number or phone:
        1. System searches households.csv
        2. If found, displays beneficiary details
        3. Fields can be pre-filled and edited (for update forms)
        """
        survey = xlsform['survey']

        # Add lookup section header
        survey.append({
            'type': 'note',
            'name': 'beneficiary_lookup_section',
            'label': '**--- Beneficiary Lookup ---**',
        })

        # Search field - ID Number
        survey.append({
            'type': 'text',
            'name': 'search_id_number',
            'label': 'Enter Beneficiary ID Number',
            'hint': 'Enter the national ID number to search for existing beneficiary',
            'required': 'no',
        })

        # Search field - Phone Number (alternative)
        survey.append({
            'type': 'text',
            'name': 'search_phone',
            'label': 'OR Enter Phone Number',
            'hint': 'Alternative: Enter phone number if ID not available',
            'required': 'no',
        })

        # Calculated field - Lookup household ID by ID number
        survey.append({
            'type': 'calculate',
            'name': 'found_hh_id_by_id',
            'calculation': "pulldata('households', 'hh_id', 'head_id_number', ${search_id_number})",
        })

        # Calculated field - Lookup household ID by phone
        survey.append({
            'type': 'calculate',
            'name': 'found_hh_id_by_phone',
            'calculation': "pulldata('households', 'hh_id', 'head_phone_number', ${search_phone})",
        })

        # Combined found ID (prefer ID lookup, fallback to phone)
        survey.append({
            'type': 'calculate',
            'name': 'found_hh_id',
            'calculation': "coalesce(${found_hh_id_by_id}, ${found_hh_id_by_phone})",
        })

        # Lookup beneficiary details using found ID
        lookup_fields = [
            ('found_name', 'head_full_name', 'Beneficiary Name'),
            ('found_first_name', 'head_first_name', 'First Name'),
            ('found_last_name', 'head_last_name', 'Last Name'),
            ('found_gender', 'head_gender', 'Gender'),
            ('found_id_number', 'head_id_number', 'ID Number'),
            ('found_phone', 'head_phone_number', 'Phone Number'),
            ('found_village', 'village_name', 'Village'),
            ('found_subcounty', 'subcounty', 'Sub-County'),
        ]

        for field_name, csv_column, label in lookup_fields:
            survey.append({
                'type': 'calculate',
                'name': field_name,
                'calculation': f"pulldata('households', '{csv_column}', 'hh_id', ${{found_hh_id}})",
            })

        # Display found beneficiary info
        survey.append({
            'type': 'note',
            'name': 'beneficiary_found_note',
            'label': '**Beneficiary Found:**\n\nName: ${found_name}\nID: ${found_id_number}\nPhone: ${found_phone}\nVillage: ${found_village}',
            'relevant': '${found_hh_id} != ""',
        })

        # Warning if not found
        survey.append({
            'type': 'note',
            'name': 'beneficiary_not_found_note',
            'label': '**No beneficiary found with this ID/Phone number.**\n\nPlease check the ID number or phone and try again.',
            'relevant': '${search_id_number} != "" and ${found_hh_id} = ""',
        })

        # Hidden field to store the matched household ID
        survey.append({
            'type': 'hidden',
            'name': 'matched_household_id',
            'default': '${found_hh_id}',
        })

        # Section divider
        survey.append({
            'type': 'note',
            'name': 'form_fields_section',
            'label': '**--- Form Fields ---**',
        })

    def _add_metadata_fields(self, survey):
        """Add standard metadata fields to survey"""
        metadata_fields = [
            {'type': 'start', 'name': 'start'},
            {'type': 'end', 'name': 'end'},
            {'type': 'deviceid', 'name': 'deviceid'},
            {'type': 'username', 'name': 'username'},
        ]

        survey.extend(metadata_fields)

    def _add_field_to_survey(self, field, xlsform):
        """
        Add a FormField to the XLSForm survey and choices

        Args:
            field: FormField instance
            xlsform: XLSForm structure being built
        """
        # Handle group/section fields specially - they need begin and end markers
        # Skip groups for now as the flat field structure doesn't support nested groups
        if field.field_type in ['group', 'section']:
            # Groups require nested structure which current model doesn't support
            # Convert to a note field instead to avoid XLSForm validation errors
            survey_row = {
                'type': 'note',
                'name': field.field_name,
                'label': f"**{field.field_label}**",  # Bold for visual separation
            }
            xlsform['survey'].append(survey_row)
            return

        survey_row = {
            'type': self._get_xlsform_type(field),
            'name': field.field_name,
            'label': field.field_label,
        }

        # Required field
        if field.required:
            survey_row['required'] = 'yes'

        # Help text
        if field.help_text:
            survey_row['hint'] = field.help_text

        # Validation
        constraint = self._build_constraint(field)
        if constraint:
            survey_row['constraint'] = constraint
            if field.validation_regex:
                survey_row['constraint_message'] = f"Invalid format for {field.field_label}"

        # Conditional display
        if field.show_if_field and field.show_if_value:
            survey_row['relevant'] = f"${{{field.show_if_field}}} = '{field.show_if_value}'"

        # Default value
        if field.default_value:
            survey_row['default'] = field.default_value

        # Handle choice fields
        if field.field_type in ['select', 'radio', 'checkbox']:
            list_name = f"{field.field_name}_list"

            # Update type with list name
            if field.field_type == 'checkbox':
                survey_row['type'] = f'select_multiple {list_name}'
            else:
                survey_row['type'] = f'select_one {list_name}'

            # Add choices
            if field.choices:
                for choice in field.choices:
                    choice_value = choice.get('value', choice)
                    choice_label = choice.get('label', choice)

                    xlsform['choices'].append({
                        'list_name': list_name,
                        'name': choice_value,
                        'label': choice_label,
                    })

        # Phone number specific constraint
        if field.field_type == 'phone':
            survey_row['constraint'] = "regex(., '^(07|01)[0-9]{8}$')"
            survey_row['constraint_message'] = "Enter valid Kenya phone number (07... or 01...)"

        xlsform['survey'].append(survey_row)

    def _get_xlsform_type(self, field):
        """Get XLSForm field type from UPG field type"""
        return self.FIELD_TYPE_MAP.get(field.field_type, 'text')

    def _build_constraint(self, field):
        """
        Build constraint expression from field validation rules

        Args:
            field: FormField instance

        Returns:
            str: XLSForm constraint expression or None
        """
        constraints = []

        # Min/max length for text fields
        if field.min_length:
            constraints.append(f"string-length(.) >= {field.min_length}")
        if field.max_length:
            constraints.append(f"string-length(.) <= {field.max_length}")

        # Min/max value for numeric fields
        if field.min_value is not None:
            constraints.append(f". >= {field.min_value}")
        if field.max_value is not None:
            constraints.append(f". <= {field.max_value}")

        # Regex validation
        if field.validation_regex:
            constraints.append(f"regex(., '{field.validation_regex}')")

        # Date constraint
        if field.field_type == 'date':
            constraints.append(". <= today()")

        # Rating constraint
        if field.field_type == 'rating':
            constraints.append(". >= 1 and . <= 5")

        return ' and '.join(constraints) if constraints else None


def check_form_has_beneficiary_lookup(form_template):
    """
    Check if a form will have beneficiary lookup enabled when synced to Kobo.

    This is useful for displaying in the UI before syncing.

    Args:
        form_template: FormTemplate instance

    Returns:
        dict: {
            'enabled': bool,
            'reason': str,
            'detected_fields': list of field names that triggered it
        }
    """
    result = {
        'enabled': False,
        'reason': '',
        'detected_fields': []
    }

    # Check form purpose first
    if form_template.form_purpose in ['program_enrollment', 'survey', 'update_details']:
        result['enabled'] = True
        result['reason'] = f"Form purpose is '{form_template.get_form_purpose_display()}'"
        return result

    # Field name patterns
    id_patterns = ['id_number', 'national_id', 'id_no', 'idnumber', 'nationalid', 'head_id_number', 'identification']
    phone_patterns = ['phone', 'phone_number', 'phonenumber', 'mobile', 'telephone', 'head_phone', 'contact_phone']
    village_patterns = ['village', 'village_name', 'villagename', 'village_id']

    detected = []

    for field in form_template.fields.all():
        if not field.required:
            continue

        field_name_lower = field.field_name.lower()
        field_label_lower = (field.field_label or '').lower()

        # Check patterns
        for pattern in id_patterns:
            if pattern in field_name_lower or pattern in field_label_lower:
                detected.append(f"{field.field_label} (ID field)")
                break

        for pattern in phone_patterns:
            if pattern in field_name_lower or pattern in field_label_lower:
                detected.append(f"{field.field_label} (Phone field)")
                break

        for pattern in village_patterns:
            if pattern in field_name_lower or pattern in field_label_lower:
                detected.append(f"{field.field_label} (Village field)")
                break

        if field.field_type == 'phone' and field.required:
            if field.field_label not in [d.split(' (')[0] for d in detected]:
                detected.append(f"{field.field_label} (Phone type)")

    if detected:
        result['enabled'] = True
        result['reason'] = "Form has mandatory identifier fields"
        result['detected_fields'] = detected

    return result


def sync_form_to_kobo(form_template, user=None, force=False):
    """
    Main function to sync FormTemplate to KoboToolbox

    Args:
        form_template: FormTemplate instance
        user: User initiating the sync (optional)
        force: Force re-sync even if already synced (default: False)

    Returns:
        tuple: (success: bool, message: str, asset_uid: str)
    """
    start_time = django_timezone.now()

    # Validation
    if not form_template.sync_to_kobo:
        return (False, "Form is not enabled for Kobo sync", None)

    if form_template.status != 'active' and not force:
        return (False, "Form must be Active to sync to Kobo", None)

    # Create sync log
    sync_log = KoboSyncLog.objects.create(
        form_template=form_template,
        sync_type='form_update' if form_template.kobo_asset_uid else 'form_create',
        status='started',
        initiated_by=user,
    )

    try:
        with transaction.atomic():
            # Initialize API client
            client = KoboAPIClient()

            # Convert form to XLSForm
            converter = XLSFormConverter(form_template)
            xlsform_content = converter.convert_to_xlsform()

            sync_log.request_data = xlsform_content
            sync_log.save()

            # Create or update asset
            if form_template.kobo_asset_uid:
                # Update existing asset
                response = client.update_asset(
                    form_template.kobo_asset_uid,
                    content=xlsform_content,
                    name=form_template.name
                )
                asset_uid = form_template.kobo_asset_uid
            else:
                # Check if asset with same name already exists in Kobo (avoid duplicates)
                existing_uid = client.find_asset_by_name(form_template.name)

                if existing_uid:
                    # Update existing asset instead of creating duplicate
                    response = client.update_asset(
                        existing_uid,
                        content=xlsform_content,
                        name=form_template.name
                    )
                    asset_uid = existing_uid
                else:
                    # Create new asset
                    response = client.create_asset(
                        name=form_template.name,
                        content=xlsform_content
                    )
                    asset_uid = response.get('uid')

                # Update form template with asset UID
                form_template.kobo_asset_uid = asset_uid
                form_template.kobo_form_url = f"{client.base_url}/#/forms/{asset_uid}"

            sync_log.kobo_asset_uid = asset_uid
            sync_log.response_data = response
            sync_log.save()

            # Deploy the asset
            try:
                deploy_response = client.deploy_asset(asset_uid)
            except requests.HTTPError as e:
                # Asset might already be deployed (400 or 405), which is OK
                if e.response.status_code not in [400, 405]:
                    raise

            # Get the correct form URL from the deployed asset
            try:
                asset_details = client.get_asset(asset_uid)
                deployment_links = asset_details.get('deployment__links', {})
                if deployment_links.get('url'):
                    form_template.kobo_form_url = deployment_links['url']
            except Exception:
                # Keep the default URL if we can't get deployment links
                pass

            # Push reference data CSVs for pulldata() validation
            try:
                push_reference_data(client, asset_uid)
            except Exception as e:
                # Non-critical error, log but don't fail
                sync_log.error_message = f"Warning: Failed to push reference data: {str(e)}"

            # Configure webhook if URL is available
            try:
                from django.urls import reverse
                from django.contrib.sites.models import Site

                # Get current site
                try:
                    site = Site.objects.get_current()
                    webhook_url = f"https://{site.domain}{reverse('forms:kobo_webhook')}"
                    client.configure_webhook(asset_uid, webhook_url)
                except Exception:
                    # Webhook configuration is optional
                    pass
            except Exception:
                pass

            # Update form template status
            form_template.kobo_sync_status = 'synced'
            form_template.last_synced_at = django_timezone.now()
            form_template.last_sync_error = ''
            form_template.save()

            # Update sync log
            sync_log.status = 'success'
            sync_log.completed_at = django_timezone.now()
            duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
            sync_log.duration_seconds = duration
            sync_log.save()

            return (True, "Form synced successfully to KoboToolbox", asset_uid)

    except Exception as e:
        # Update form template with error
        form_template.kobo_sync_status = 'sync_failed'
        form_template.last_sync_error = str(e)
        form_template.save()

        # Update sync log
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        sync_log.completed_at = django_timezone.now()
        duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
        sync_log.duration_seconds = duration
        sync_log.save()

        return (False, f"Sync failed: {str(e)}", None)


def fetch_kobo_submissions(form_template, user=None):
    """
    Manually fetch submissions from KoboToolbox for a form.
    Use this when webhooks aren't available (e.g., localhost).

    Includes MIS validation based on form_purpose:
    - general: No validation
    - new_registration: Warn if beneficiary exists (duplicate)
    - program_enrollment: Link to existing beneficiary
    - survey: Link to existing beneficiary
    - update_details: Update existing beneficiary data

    Args:
        form_template: FormTemplate instance with kobo_asset_uid
        user: User initiating the fetch (optional)

    Returns:
        tuple: (success: bool, message: str, count: int)
    """
    from .models import FormSubmission, KoboWebhookLog
    from .beneficiary_lookup import validate_submission_for_purpose, update_household_from_submission
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not form_template.kobo_asset_uid:
        return (False, "Form not synced to KoboToolbox", 0)

    try:
        client = KoboAPIClient()
        asset_uid = form_template.kobo_asset_uid

        # Fetch submissions from Kobo API
        url = f"{client.api_url}/assets/{asset_uid}/data/"
        response = requests.get(url, headers=client.headers, timeout=60)
        response.raise_for_status()

        data = response.json()
        submissions = data.get('results', [])

        new_count = 0
        skipped_count = 0
        duplicates_found = 0
        updates_made = 0

        for sub in submissions:
            submission_uuid = sub.get('_uuid')

            # Skip if already imported
            if FormSubmission.objects.filter(kobo_submission_uuid=submission_uuid).exists():
                skipped_count += 1
                continue

            # Parse submission time (ensure timezone-aware)
            submission_time = None
            if sub.get('_submission_time'):
                try:
                    from datetime import datetime
                    dt_str = sub['_submission_time'].replace('Z', '+00:00')
                    parsed_dt = datetime.fromisoformat(dt_str)
                    # Ensure timezone-aware
                    if parsed_dt.tzinfo is None:
                        submission_time = django_timezone.make_aware(parsed_dt)
                    else:
                        submission_time = parsed_dt
                except Exception:
                    submission_time = django_timezone.now()

            # Find submitter
            submitted_by = user or form_template.created_by
            kobo_username = sub.get('_submitted_by')
            if kobo_username:
                found_user = User.objects.filter(username=kobo_username).first()
                if found_user:
                    submitted_by = found_user

            # Extract GPS data
            gps_lat, gps_lng = None, None
            for key in ['gps_location', 'location', 'household_gps', 'geopoint']:
                if key in sub and sub[key]:
                    parts = str(sub[key]).split()
                    if len(parts) >= 2:
                        try:
                            gps_lat = float(parts[0])
                            gps_lng = float(parts[1])
                            break
                        except ValueError:
                            pass

            # Build form_data (exclude internal Kobo fields)
            form_data = {k: v for k, v in sub.items() if not k.startswith('_')}

            # MIS Validation based on form purpose
            validation_result = validate_submission_for_purpose(form_template, form_data)
            validation_status = validation_result['status']
            validation_message = validation_result['message']
            matched_household = validation_result['household']

            # Handle updates for update_details forms
            if validation_result['should_update'] and matched_household:
                success, updated_fields, update_msg = update_household_from_submission(
                    matched_household,
                    form_data,
                    form_template.field_mapping
                )
                if success and updated_fields:
                    validation_status = 'data_updated'
                    validation_message = f'{validation_message}. {update_msg}'
                    updates_made += 1

            # Track duplicates for new_registration forms
            if validation_status == 'duplicate_detected':
                duplicates_found += 1

            # Create submission with validation info
            FormSubmission.objects.create(
                form_template=form_template,
                submitted_by=submitted_by,
                form_data=form_data,
                gps_latitude=gps_lat,
                gps_longitude=gps_lng,
                status='submitted',
                kobo_submission_uuid=submission_uuid,
                kobo_submission_time=submission_time,
                data_source='kobo_sync',
                # MIS validation fields
                validation_status=validation_status,
                validation_message=validation_message,
                matched_household=matched_household,
                # Link to household if found (for surveys/enrollments)
                household=matched_household if matched_household and form_template.form_purpose in ['survey', 'program_enrollment'] else None,
            )
            new_count += 1

        # Build result message
        msg_parts = [f"Fetched {new_count} new submissions"]
        if skipped_count:
            msg_parts.append(f"{skipped_count} already imported")
        if duplicates_found:
            msg_parts.append(f"{duplicates_found} duplicates detected")
        if updates_made:
            msg_parts.append(f"{updates_made} beneficiary records updated")

        return (True, " | ".join(msg_parts), new_count)

    except requests.HTTPError as e:
        return (False, f"KoboToolbox API error: {e.response.status_code} - {e.response.text[:200]}", 0)
    except Exception as e:
        return (False, f"Error fetching submissions: {str(e)}", 0)


def push_reference_data(client, asset_uid):
    """
    Push reference data CSVs to KoboToolbox asset for pulldata() validation

    Args:
        client: KoboAPIClient instance
        asset_uid: KoboToolbox asset UID
    """
    # Export reference data CSV files
    reference_files = {
        'households.csv': export_households_csv_content(),
        'villages.csv': export_villages_csv_content(),
        'business_groups.csv': export_business_groups_csv_content(),
        'mentors.csv': export_mentors_csv_content(),
    }

    # Upload each file to the asset
    for filename, content in reference_files.items():
        if content:
            try:
                client.upload_media_file(asset_uid, filename, content)
            except Exception as e:
                # Log but don't fail if one file upload fails
                print(f"Warning: Failed to upload {filename}: {str(e)}")


def export_households_csv_content():
    """
    Export households as CSV string for Kobo pulldata()

    This CSV enables beneficiary lookup and pre-fill in KoboCollect:
    - User enters ID number or phone number
    - Form uses pulldata() to fetch and display existing beneficiary data
    - User can verify and update information

    Columns match common XLSForm pulldata() patterns.
    """
    from households.models import Household
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Extended headers for comprehensive beneficiary lookup and pre-fill
    writer.writerow([
        'hh_id',              # Primary lookup key
        'hh_name',            # Household name/identifier
        'head_id_number',     # ID number (primary search field)
        'head_phone_number',  # Phone number (secondary search field)
        'head_first_name',    # First name for pre-fill
        'head_middle_name',   # Middle name for pre-fill
        'head_last_name',     # Last name for pre-fill
        'head_full_name',     # Full name display
        'head_gender',        # Gender for pre-fill
        'head_dob',           # Date of birth for pre-fill
        'village_id',         # Village ID for cascading select
        'village_name',       # Village name display
        'subcounty',          # Sub-county for display
        'county',             # County for display
        'gps_latitude',       # GPS for map display
        'gps_longitude',      # GPS for map display
        'phone_alt',          # Alternative phone (legacy field)
        'national_id_alt',    # Alternative ID (legacy field)
    ])

    # Data rows with all fields for pre-fill
    households = Household.objects.select_related(
        'village',
        'village__subcounty_obj',
        'village__subcounty_obj__county'
    ).all()

    for hh in households:
        # Get geographic hierarchy
        village_name = hh.village.name if hh.village else ''
        subcounty = ''
        county = ''
        if hh.village and hasattr(hh.village, 'subcounty_obj') and hh.village.subcounty_obj:
            subcounty = hh.village.subcounty_obj.name
            if hh.village.subcounty_obj.county:
                county = hh.village.subcounty_obj.county.name

        # Format date of birth
        dob = ''
        if hh.head_date_of_birth:
            dob = hh.head_date_of_birth.isoformat()

        writer.writerow([
            hh.id,
            hh.name or '',
            hh.head_id_number or hh.national_id or '',
            hh.head_phone_number or hh.phone_number or '',
            hh.head_first_name or '',
            hh.head_middle_name or '',
            hh.head_last_name or '',
            hh.head_full_name or hh.name or '',
            hh.head_gender or '',
            dob,
            hh.village_id or '',
            village_name,
            subcounty,
            county,
            hh.gps_latitude or '',
            hh.gps_longitude or '',
            hh.phone_number or '',      # Legacy/alternative phone
            hh.national_id or '',       # Legacy/alternative ID
        ])

    return output.getvalue()


def export_villages_csv_content():
    """Export villages as CSV string for Kobo pulldata()"""
    from core.models import Village
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(['village_id', 'village_name', 'subcounty', 'county'])

    # Data rows - use subcounty_obj (actual field name in model)
    villages = Village.objects.select_related('subcounty_obj', 'subcounty_obj__county').all()
    for village in villages:
        subcounty = getattr(village, 'subcounty_obj', None) or getattr(village, 'subcounty', None)
        writer.writerow([
            village.id,
            village.name,
            subcounty.name if subcounty else '',
            subcounty.county.name if subcounty and hasattr(subcounty, 'county') and subcounty.county else '',
        ])

    return output.getvalue()


def export_business_groups_csv_content():
    """Export business groups as CSV string for Kobo pulldata()"""
    from business_groups.models import BusinessGroup
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(['bg_id', 'bg_name', 'business_type', 'status'])

    # Data rows
    groups = BusinessGroup.objects.all()
    for group in groups:
        writer.writerow([
            group.id,
            group.name,
            group.business_type or '',
            group.status or '',
        ])

    return output.getvalue()


def export_mentors_csv_content():
    """Export mentors as CSV string for Kobo pulldata()"""
    from core.models import Mentor
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(['mentor_id', 'mentor_name', 'phone_number', 'village_name'])

    # Data rows
    mentors = Mentor.objects.select_related('user', 'village').all()
    for mentor in mentors:
        writer.writerow([
            mentor.id,
            mentor.user.get_full_name() if mentor.user else '',
            mentor.user.phone_number if mentor.user else '',
            mentor.village.name if mentor.village else '',
        ])

    return output.getvalue()
