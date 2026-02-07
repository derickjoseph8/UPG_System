"""
Dynamic Forms System for UPG Management
Allows M&E staff to create editable forms/surveys and assign them to field associates/mentors
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class FormTemplate(models.Model):
    """
    Dynamic form template created by M&E staff
    """
    FORM_TYPE_CHOICES = [
        ('household_survey', 'Household Survey'),
        ('business_survey', 'Business Progress Survey'),
        ('ppi_assessment', 'PPI Assessment'),
        ('baseline_survey', 'Baseline Survey'),
        ('midline_survey', 'Midline Survey'),
        ('endline_survey', 'Endline Survey'),
        ('training_evaluation', 'Training Evaluation'),
        ('mentoring_report', 'Mentoring Report'),
        ('custom_form', 'Custom Form'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    FORM_PURPOSE_CHOICES = [
        ('general', 'General Form (No Validation)'),
        ('new_registration', 'New Beneficiary Registration'),
        ('program_enrollment', 'Program Enrollment'),
        ('survey', 'Survey/Assessment'),
        ('update_details', 'Update Beneficiary Details'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=30, choices=FORM_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Form structure stored as JSON
    form_fields = models.JSONField(default=list, help_text="JSON structure defining form fields")

    # Assignment and workflow
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Form settings
    allow_multiple_submissions = models.BooleanField(default=False)
    require_photo_evidence = models.BooleanField(default=False)
    require_gps_location = models.BooleanField(default=False)
    auto_assign_to_mentors = models.BooleanField(default=False)

    # KoboToolbox Integration Fields
    sync_to_kobo = models.BooleanField(
        default=False,
        help_text="Enable sync with KoboToolbox for offline data collection"
    )
    kobo_asset_uid = models.CharField(
        max_length=100,
        blank=True,
        help_text="KoboToolbox Asset UID (auto-generated on sync)"
    )
    kobo_form_url = models.URLField(
        blank=True,
        help_text="Direct link to form in KoboToolbox"
    )
    kobo_sync_status = models.CharField(
        max_length=20,
        choices=[
            ('never_synced', 'Never Synced'),
            ('synced', 'Synced'),
            ('sync_pending', 'Sync Pending'),
            ('sync_failed', 'Sync Failed'),
            ('sync_outdated', 'Sync Outdated'),
        ],
        default='never_synced',
        help_text="Current sync status with KoboToolbox"
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last successful sync to Kobo"
    )
    last_sync_error = models.TextField(
        blank=True,
        help_text="Last sync error message if failed"
    )
    kobo_version = models.IntegerField(
        default=1,
        help_text="Version counter for tracking form updates"
    )

    # MIS Integration Settings
    form_purpose = models.CharField(
        max_length=30,
        choices=FORM_PURPOSE_CHOICES,
        default='general',
        help_text="Determines how submissions are validated against MIS data"
    )
    field_mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text="Maps form field names to MIS fields for validation. Example: {'id_number': 'head_id_number', 'phone': 'head_phone_number', 'village': 'village'}"
    )

    def __str__(self):
        return f"{self.name} ({self.get_form_type_display()})"

    def save(self, *args, **kwargs):
        """
        Override save to handle Kobo sync status and versioning.
        When a synced form is updated, mark it as outdated and increment version.
        """
        # Check if this is an update (not a new form)
        if self.pk:
            # Get the original form to detect changes
            try:
                original = FormTemplate.objects.get(pk=self.pk)

                # Check if form content has changed (fields that affect Kobo form)
                content_changed = (
                    original.name != self.name or
                    original.form_fields != self.form_fields or
                    original.form_type != self.form_type
                )

                # If form was synced and content changed, mark as outdated
                if content_changed and original.kobo_asset_uid and original.kobo_sync_status == 'synced':
                    self.kobo_sync_status = 'sync_outdated'
                    self.kobo_version = original.kobo_version + 1

            except FormTemplate.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def needs_resync(self):
        """Check if form needs to be resynced to Kobo"""
        return (
            self.sync_to_kobo and
            self.kobo_asset_uid and
            self.kobo_sync_status in ['sync_outdated', 'sync_pending', 'sync_failed']
        )

    class Meta:
        db_table = 'upg_form_templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sync_to_kobo', 'kobo_sync_status']),
            models.Index(fields=['kobo_asset_uid']),
        ]


class FormAssignment(models.Model):
    """
    Assignment of forms to field associates or mentors
    """
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    ASSIGNMENT_TYPE_CHOICES = [
        ('direct_to_mentor', 'Direct to Mentor'),
        ('via_field_associate', 'Via Field Associate'),
    ]

    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_assignments_made')

    # Assignment can be to field associate who then assigns to mentors, or directly to mentor
    assignment_type = models.CharField(max_length=30, choices=ASSIGNMENT_TYPE_CHOICES)
    field_associate = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='assigned_forms',
                                       limit_choices_to={'role': 'field_associate'})
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='assigned_forms_mentor',
                              limit_choices_to={'role': 'mentor'})

    # Assignment details
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')

    # Status tracking
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Target criteria (optional filters for which households/groups to survey)
    target_villages = models.JSONField(default=list, blank=True)
    target_households = models.JSONField(default=list, blank=True)
    target_business_groups = models.JSONField(default=list, blank=True)
    min_submissions_required = models.IntegerField(default=1)

    def __str__(self):
        assignee = self.mentor or self.field_associate
        return f"{self.title} -> {assignee.get_full_name() if assignee else 'Unassigned'}"

    def clean(self):
        if self.assignment_type == 'direct_to_mentor' and not self.mentor:
            raise ValidationError("Mentor is required for direct assignments")
        if self.assignment_type == 'via_field_associate' and not self.field_associate:
            raise ValidationError("Field associate is required for field associate assignments")

    class Meta:
        db_table = 'upg_form_assignments'
        ordering = ['-assigned_at']


class FormSubmission(models.Model):
    """
    Individual form submissions by mentors
    """
    SUBMISSION_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    assignment = models.ForeignKey(
        FormAssignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        null=True,  # Allow null for Kobo submissions without assignment
        blank=True
    )
    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='submissions')

    # Submitter details
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_submissions')
    submission_date = models.DateTimeField(auto_now_add=True)

    # Form data stored as JSON
    form_data = models.JSONField(default=dict)

    # Optional attachments
    photo_evidence = models.ImageField(upload_to='form_submissions/photos/', null=True, blank=True)
    document_attachment = models.FileField(upload_to='form_submissions/docs/', null=True, blank=True)

    # Location data
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_name = models.CharField(max_length=200, blank=True)

    # Review and approval
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS_CHOICES, default='draft')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Related entities (optional)
    household = models.ForeignKey('households.Household', on_delete=models.SET_NULL, null=True, blank=True)
    business_group = models.ForeignKey('business_groups.BusinessGroup', on_delete=models.SET_NULL, null=True, blank=True)

    # MIS Validation Status
    VALIDATION_STATUS_CHOICES = [
        ('not_validated', 'Not Validated'),
        ('beneficiary_found', 'Beneficiary Found'),
        ('beneficiary_not_found', 'Beneficiary Not Found'),
        ('duplicate_detected', 'Duplicate Detected'),
        ('data_updated', 'Data Updated'),
    ]
    validation_status = models.CharField(
        max_length=30,
        choices=VALIDATION_STATUS_CHOICES,
        default='not_validated',
        help_text="Result of MIS validation check"
    )
    validation_message = models.TextField(
        blank=True,
        help_text="Details about the validation result"
    )
    matched_household = models.ForeignKey(
        'households.Household',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_matches',
        help_text="Household matched during validation"
    )

    # KoboToolbox source tracking
    kobo_submission_uuid = models.CharField(
        max_length=100,
        null=True,  # Allow null for web submissions
        blank=True,
        unique=True,
        help_text="UUID from KoboToolbox submission"
    )
    kobo_submission_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Original submission timestamp from Kobo"
    )
    data_source = models.CharField(
        max_length=20,
        choices=[
            ('web_form', 'Web Form'),
            ('kobo_sync', 'KoboToolbox Sync'),
            ('mobile_app', 'Mobile App'),
            ('api', 'API'),
        ],
        default='web_form',
        help_text="Source of this submission"
    )

    def __str__(self):
        return f"{self.form_template.name} - {self.submitted_by.get_full_name()} - {self.submission_date.strftime('%Y-%m-%d')}"

    class Meta:
        db_table = 'upg_form_submissions'
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['kobo_submission_uuid']),
            models.Index(fields=['data_source']),
        ]


class FormField(models.Model):
    """
    Individual form field definition for building dynamic forms
    """
    FIELD_TYPE_CHOICES = [
        # Text Fields
        ('text', 'Text Input (Short)'),
        ('textarea', 'Text Area (Long)'),
        ('note', 'Note/Display Text'),

        # Numeric Fields
        ('number', 'Number Input'),
        ('decimal', 'Decimal Number'),
        ('calculate', 'Calculated Field'),

        # Contact Fields
        ('email', 'Email Input'),
        ('phone', 'Phone Number'),

        # Date/Time Fields
        ('date', 'Date Picker'),
        ('time', 'Time Picker'),
        ('datetime', 'Date & Time'),

        # Choice Fields
        ('select', 'Dropdown Select'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes (Multiple)'),
        ('boolean', 'Yes/No'),

        # Media Fields
        ('file', 'File Upload'),
        ('image', 'Image/Photo Upload'),
        ('audio', 'Audio Recording'),
        ('video', 'Video Recording'),

        # Special Fields
        ('rating', 'Rating Scale (1-5)'),
        ('location', 'GPS Location (Lat/Long)'),
        ('signature', 'Digital Signature'),
        ('barcode', 'Barcode/QR Scanner'),
        ('range', 'Range Slider'),

        # Organizational
        ('section', 'Section Header'),
        ('group', 'Field Group'),
    ]

    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=500)  # Increased for long Kobo labels
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)

    # Field configuration
    required = models.BooleanField(default=False)
    help_text = models.CharField(max_length=500, blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    default_value = models.CharField(max_length=500, blank=True)

    # For select, radio, checkbox fields
    choices = models.JSONField(default=list, blank=True, help_text="List of choices for select/radio/checkbox fields")

    # Field validation
    min_length = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    min_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    validation_regex = models.CharField(max_length=500, blank=True)

    # Display order
    order = models.IntegerField(default=0)

    # Conditional display
    show_if_field = models.CharField(max_length=100, blank=True, help_text="Show this field only if another field has specific value")
    show_if_value = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.form_template.name} - {self.field_label}"

    @property
    def options(self):
        """
        Returns formatted choices for select/radio/checkbox fields.
        Handles both simple lists ['opt1', 'opt2'] and dict lists [{'value': 'v1', 'label': 'L1'}]
        """
        if not self.choices:
            return []

        options = []
        for choice in self.choices:
            if isinstance(choice, dict):
                options.append({
                    'value': choice.get('value', choice.get('name', '')),
                    'label': choice.get('label', choice.get('value', choice.get('name', '')))
                })
            else:
                # Simple string choice
                options.append({'value': str(choice), 'label': str(choice)})
        return options

    class Meta:
        db_table = 'upg_form_fields'
        ordering = ['order', 'id']


class FormAssignmentMentor(models.Model):
    """
    Many-to-many relationship for field associates assigning forms to multiple mentors
    """
    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, related_name='mentor_assignments')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mentor'})
    assigned_by_fa = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fa_mentor_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    instructions = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.assignment.title} -> {self.mentor.get_full_name()}"

    class Meta:
        db_table = 'upg_form_assignment_mentors'
        unique_together = ['assignment', 'mentor']


class KoboSyncLog(models.Model):
    """
    Log of KoboToolbox synchronization operations
    Tracks all sync activities for audit and debugging
    """
    SYNC_TYPE_CHOICES = [
        ('form_create', 'Form Create'),
        ('form_update', 'Form Update'),
        ('form_delete', 'Form Delete'),
        ('reference_data_push', 'Reference Data Push'),
        ('submission_receive', 'Submission Receive'),
    ]

    STATUS_CHOICES = [
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ]

    form_template = models.ForeignKey(
        FormTemplate,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sync_logs'
    )

    sync_type = models.CharField(max_length=30, choices=SYNC_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # Details
    kobo_asset_uid = models.CharField(max_length=100, blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Metadata
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.get_sync_type_display()} - {self.get_status_display()} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        db_table = 'upg_kobo_sync_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['sync_type', 'status']),
            models.Index(fields=['started_at']),
        ]


class FormFieldAssociate(models.Model):
    """
    Assignment of form template to Field Associates
    Creator (PM/M&E) assigns FA who then assigns mentors
    Consistent with Program and Training hierarchy
    """
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending - Awaiting Mentor Assignment'),
        ('assigned', 'Assigned - Mentors Added'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    form_template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fa_assignments')
    field_associate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_fa_assignments',
                                        limit_choices_to={'role': 'field_associate'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='form_fa_assignments_made')

    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.form_template.name} -> FA: {self.field_associate.get_full_name()}"

    @property
    def mentor_count(self):
        return self.mentor_assignments.count()

    class Meta:
        db_table = 'upg_form_field_associates'
        unique_together = ['form_template', 'field_associate']


class FormMentorAssignment(models.Model):
    """
    Assignment of form template to Mentors via Field Associate
    FA assigns mentors under them to the form
    Consistent with Program and Training hierarchy
    """
    form_fa = models.ForeignKey(FormFieldAssociate, on_delete=models.CASCADE, related_name='mentor_assignments')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_mentor_assignments',
                              limit_choices_to={'role': 'mentor'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='form_mentor_assignments_made')

    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.form_fa.form_template.name} -> Mentor: {self.mentor.get_full_name()}"

    class Meta:
        db_table = 'upg_form_mentor_assignments'
        unique_together = ['form_fa', 'mentor']


class KoboWebhookLog(models.Model):
    """
    Log of webhook requests received from KoboToolbox
    Tracks incoming form submissions for processing
    """
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('duplicate', 'Duplicate'),
    ]

    kobo_asset_uid = models.CharField(max_length=100)
    submission_uuid = models.CharField(max_length=100, unique=True)

    # Raw webhook data
    raw_payload = models.JSONField(default=dict)
    processed_data = models.JSONField(default=dict, blank=True)

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    error_message = models.TextField(blank=True)

    # Linked records
    form_template = models.ForeignKey(
        FormTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    form_submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Metadata
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.submission_uuid} - {self.get_status_display()} - {self.received_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        db_table = 'upg_kobo_webhook_logs'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['kobo_asset_uid']),
            models.Index(fields=['submission_uuid']),
            models.Index(fields=['status']),
        ]
