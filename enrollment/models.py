"""
Enrollment and Targeting models for UPG Kenya
Adapted from Kaduna system with Kenya-specific validation (ID number and phone number)
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from households.models import Household
from core.models import Village, Program

User = get_user_model()


class ApplicationStatus(models.TextChoices):
    """Enrollment application status"""
    SUBMITTED = 'submitted', 'Submitted'
    SCREENING = 'screening', 'Screening'
    ID_VALIDATION = 'id_validation', 'ID Validation'
    VERIFICATION = 'verification', 'Field Verification'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ENROLLED = 'enrolled', 'Enrolled'
    WAITLISTED = 'waitlisted', 'Waitlisted'
    WITHDRAWN = 'withdrawn', 'Withdrawn'


class VerificationStatus(models.TextChoices):
    """Verification status"""
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    VERIFIED = 'verified', 'Verified'
    REJECTED = 'rejected', 'Rejected'
    NEEDS_REVIEW = 'needs_review', 'Needs Review'


class RuleCategory(models.TextChoices):
    """Categories for targeting rules"""
    DEMOGRAPHIC = 'demographic', 'Demographic'  # Age, gender, marital status
    ECONOMIC = 'economic', 'Economic'  # Income, poverty score, assets
    GEOGRAPHIC = 'geographic', 'Geographic'  # County, sub-county, village
    VULNERABILITY = 'vulnerability', 'Vulnerability'  # Disability, female-headed, orphans
    PROGRAM = 'program', 'Program'  # Not in other programs, first-time beneficiary
    HOUSEHOLD = 'household', 'Household'  # Household size, composition
    EXCLUSION = 'exclusion', 'Exclusion'  # Rules that disqualify


class RuleOperator(models.TextChoices):
    """Operators for rule evaluation"""
    EQUALS = 'equals', 'Equals'
    NOT_EQUALS = 'not_equals', 'Not Equals'
    GREATER_THAN = 'greater_than', 'Greater Than'
    GREATER_THAN_OR_EQUAL = 'gte', 'Greater Than or Equal'
    LESS_THAN = 'less_than', 'Less Than'
    LESS_THAN_OR_EQUAL = 'lte', 'Less Than or Equal'
    IN = 'in', 'In'
    NOT_IN = 'not_in', 'Not In'
    BETWEEN = 'between', 'Between'
    CONTAINS = 'contains', 'Contains'
    IS_NULL = 'is_null', 'Is Null'
    IS_NOT_NULL = 'is_not_null', 'Is Not Null'


class TargetingRuleGroup(models.Model):
    """Group of targeting rules with AND/OR logic"""
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='rule_groups')

    # Group logic
    logic_operator = models.CharField(max_length=10, default='AND', choices=[('AND', 'AND'), ('OR', 'OR')])
    priority = models.IntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)

    # Scoring
    group_weight = models.FloatField(default=1.0)
    min_rules_to_pass = models.IntegerField(null=True, blank=True)  # For OR logic

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.program.name}"

    class Meta:
        db_table = 'upg_targeting_rule_groups'
        ordering = ['priority', 'name']


class TargetingRule(models.Model):
    """Targeting/Eligibility rule configuration"""
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='targeting_rules', null=True, blank=True)
    rule_group = models.ForeignKey(TargetingRuleGroup, on_delete=models.CASCADE, related_name='rules', null=True, blank=True)

    # Rule categorization
    category = models.CharField(max_length=20, choices=RuleCategory.choices, default=RuleCategory.DEMOGRAPHIC)

    # Rule configuration
    rule_type = models.CharField(max_length=50)  # e.g., "age", "poverty_score", "village", "gender"
    field_path = models.CharField(max_length=200, null=True, blank=True)  # JSON path for nested data
    operator = models.CharField(max_length=20, choices=RuleOperator.choices, default=RuleOperator.EQUALS)
    value = models.JSONField()  # Value to compare against
    value_type = models.CharField(max_length=20, default='string')  # string, number, boolean, date, array

    # Priority and weighting
    priority = models.IntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    weight = models.FloatField(default=1.0)
    score_on_pass = models.FloatField(default=10.0)  # Points awarded when rule passes
    score_on_fail = models.FloatField(default=0.0)  # Points when rule fails

    # Error handling
    error_message = models.CharField(max_length=500, null=True, blank=True)
    allow_override = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    class Meta:
        db_table = 'upg_targeting_rules'
        ordering = ['priority', 'name']


class EnrollmentApplication(models.Model):
    """Enrollment application tracking"""
    application_id = models.CharField(max_length=50, unique=True, db_index=True)

    # Applicant info (stored before household record creation)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)

    # Kenya-specific validation fields
    id_number = models.CharField(max_length=20, db_index=True, help_text="National ID or Birth Certificate Number")
    phone_number = models.CharField(max_length=20, help_text="Phone number for validation")
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, related_name='enrollment_applications')

    # Application data
    application_data = models.JSONField(null=True, blank=True)

    # Program assignment
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, related_name='applications')

    # Workflow status
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.SUBMITTED, db_index=True)
    current_step = models.CharField(max_length=50, null=True, blank=True)

    # Screening
    screening_score = models.FloatField(null=True, blank=True)
    screening_passed = models.BooleanField(null=True, blank=True)
    screening_date = models.DateTimeField(null=True, blank=True)
    screening_notes = models.TextField(null=True, blank=True)

    # ID Validation (Kenya-specific)
    id_validated = models.BooleanField(null=True, blank=True)
    id_validation_date = models.DateTimeField(null=True, blank=True)
    id_validation_response = models.JSONField(null=True, blank=True)

    # Phone Validation (Kenya-specific)
    phone_validated = models.BooleanField(null=True, blank=True)
    phone_validation_date = models.DateTimeField(null=True, blank=True)

    # Poverty Score
    poverty_score = models.FloatField(null=True, blank=True)
    poverty_score_fetched_date = models.DateTimeField(null=True, blank=True)

    # Approval
    approved = models.BooleanField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='enrollment_approved_applications')
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    # Linked household (created after enrollment)
    household = models.ForeignKey(Household, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollment_applications')

    # Submitted by
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='enrollment_submitted_applications')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_id} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.application_id:
            # Generate application ID: APP-YYYY-NNNNN
            from datetime import datetime
            year = datetime.now().year
            last_app = EnrollmentApplication.objects.filter(
                application_id__startswith=f'APP-{year}-'
            ).order_by('-created_at').first()

            if last_app:
                last_num = int(last_app.application_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.application_id = f'APP-{year}-{new_num:05d}'

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'upg_enrollment_applications'
        ordering = ['-created_at']


class Verification(models.Model):
    """Field verification record"""
    application = models.ForeignKey(EnrollmentApplication, on_delete=models.CASCADE, related_name='verifications')

    # Verification details
    status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    verification_type = models.CharField(max_length=50)  # e.g., "field_visit", "document", "household"
    verification_date = models.DateTimeField(null=True, blank=True)

    # Field officer
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verifications')

    # Verification data
    checklist = models.JSONField(null=True, blank=True)  # Verification checklist items
    findings = models.TextField(null=True, blank=True)
    recommendation = models.CharField(max_length=50, null=True, blank=True)

    # Evidence
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo_urls = models.JSONField(null=True, blank=True)  # Array of photo URLs

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Verification for {self.application.application_id} - {self.get_status_display()}"

    class Meta:
        db_table = 'upg_verifications'
        ordering = ['-created_at']
