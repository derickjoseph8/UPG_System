"""
Training and Mentoring Models
Enhanced with features from Kaduna system
"""

from django.db import models
from django.contrib.auth import get_user_model
from households.models import Household
from core.models import BusinessMentorCycle, Program

User = get_user_model()


class ModuleStatus(models.TextChoices):
    """Training module status"""
    DRAFT = 'draft', 'Draft'
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'


class SessionStatus(models.TextChoices):
    """Training session status"""
    SCHEDULED = 'scheduled', 'Scheduled'
    ONGOING = 'ongoing', 'Ongoing'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    POSTPONED = 'postponed', 'Postponed'


class TrainingModule(models.Model):
    """
    Training module configuration
    New model from Kaduna system for structured training modules
    """
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    # Program association
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='training_modules', null=True, blank=True)

    # Module details
    module_number = models.IntegerField(help_text="Order in sequence")
    duration_days = models.IntegerField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)

    # Content
    topics = models.JSONField(default=list, blank=True, help_text="List of topics covered")
    materials_url = models.CharField(max_length=500, null=True, blank=True)
    assessment_required = models.BooleanField(default=False)

    # Prerequisites
    prerequisite_module = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_modules')
    is_sequential = models.BooleanField(default=True, help_text="Must complete previous module before this")

    # Status
    status = models.CharField(max_length=20, choices=ModuleStatus.choices, default=ModuleStatus.DRAFT)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        db_table = 'upg_training_modules'
        ordering = ['module_number', 'name']


class TrainingSession(models.Model):
    """
    Training session record
    New model from Kaduna system for individual training sessions
    """
    session_id = models.CharField(max_length=50, unique=True, db_index=True)

    # Module
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='sessions')

    # Program
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, related_name='training_sessions')

    # Schedule
    session_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)

    # Location
    venue = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.CharField(max_length=500, null=True, blank=True)

    # Attendance
    expected_participants = models.IntegerField(default=0)
    actual_participants = models.IntegerField(default=0)

    # Facilitator
    facilitator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='facilitated_sessions')
    facilitator_name = models.CharField(max_length=200, null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=SessionStatus.choices, default=SessionStatus.SCHEDULED, db_index=True)

    # Notes
    session_notes = models.TextField(null=True, blank=True)
    challenges = models.TextField(null=True, blank=True)
    photo_urls = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.session_id} - {self.module.name} - {self.session_date}"

    def save(self, *args, **kwargs):
        if not self.session_id:
            # Generate session ID: SES-YYYY-NNNNN
            from datetime import datetime
            year = datetime.now().year
            last_session = TrainingSession.objects.filter(
                session_id__startswith=f'SES-{year}-'
            ).order_by('-created_at').first()

            if last_session:
                last_num = int(last_session.session_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.session_id = f'SES-{year}-{new_num:05d}'

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'upg_training_sessions'
        ordering = ['-session_date', 'start_time']


class SessionAttendance(models.Model):
    """
    Training session attendance record
    New model from Kaduna for tracking individual session attendance
    """
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='session_attendance')
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='training_session_attendance')

    # Attendance
    attended = models.BooleanField(default=False)
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    attendance_type = models.CharField(max_length=50, default='full', null=True, blank=True)  # full, partial, absent

    # Assessment (if applicable)
    assessment_score = models.FloatField(null=True, blank=True)
    assessment_passed = models.BooleanField(null=True, blank=True)

    # Notes
    notes = models.TextField(null=True, blank=True)

    # Recorded by
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_session_attendance')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.household.name} - {self.session.session_id} - {'Present' if self.attended else 'Absent'}"

    class Meta:
        db_table = 'upg_session_attendance'
        unique_together = ['session', 'household']
        ordering = ['-session__session_date']


class Training(models.Model):
    """
    Training modules and sessions associated with BM Cycles
    """
    TRAINING_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    module_id = models.CharField(max_length=50)
    module_number = models.IntegerField(help_text="Sequential module number (1, 2, 3, etc.)", null=True, blank=True)
    bm_cycle = models.ForeignKey(BusinessMentorCycle, on_delete=models.CASCADE, related_name='trainings', null=True, blank=True)
    assigned_mentor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mentor'}, null=True, blank=True)

    # Enhanced training details from meeting notes
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1, help_text="Training length in hours", null=True, blank=True)
    location = models.CharField(max_length=200, help_text="Training location/venue", blank=True)
    participant_count = models.IntegerField(help_text="Actual number of participants", null=True, blank=True)

    time_taken = models.DurationField(help_text="Training duration", null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TRAINING_STATUS_CHOICES, default='planned')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    training_dates = models.JSONField(default=list, blank=True, help_text="List of specific training session dates")
    max_households = models.IntegerField(default=25, help_text="Maximum households per training")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.bm_cycle:
            return f"{self.name} - {self.bm_cycle.bm_cycle_name}"
        return self.name

    @property
    def enrolled_households_count(self):
        return self.attendances.values('household').distinct().count()

    @property
    def available_slots(self):
        return self.max_households - self.enrolled_households_count

    class Meta:
        db_table = 'upg_trainings'
        indexes = [
            models.Index(fields=['bm_cycle']),
            models.Index(fields=['assigned_mentor']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
        ]


class TrainingAttendance(models.Model):
    """
    Training attendance tracking
    """
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='attendances')
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    attendance = models.BooleanField(default=True)
    training_date = models.DateField()

    # Track who marked attendance and when
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='marked_attendances',
                                 help_text="Mentor who marked this attendance")
    attendance_marked_at = models.DateTimeField(null=True, blank=True,
                                              help_text="When attendance was last updated")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.training.name}"

    class Meta:
        db_table = 'upg_training_attendances'
        unique_together = ['training', 'household', 'training_date']  # Prevent duplicate attendance records
        indexes = [
            models.Index(fields=['training_date']),
            models.Index(fields=['attendance']),
        ]


class MentoringVisit(models.Model):
    """
    Mentoring visit tracking
    Enhanced with features from Kaduna system
    """
    VISIT_TYPE_CHOICES = [
        ('scheduled', 'Scheduled Visit'),
        ('follow_up', 'Follow-up Visit'),
        ('emergency', 'Emergency Visit'),
        ('on_site', 'On-site'),
        ('phone', 'Phone Check'),
        ('virtual', 'Virtual'),
    ]

    BUSINESS_STATUS_CHOICES = [
        ('thriving', 'Thriving'),
        ('stable', 'Stable'),
        ('struggling', 'Struggling'),
        ('closed', 'Closed'),
        ('not_started', 'Not Started'),
    ]

    visit_id = models.CharField(max_length=50, unique=True, db_index=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='mentoring_visits')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentoring_visits')

    # Visit details
    topic = models.CharField(max_length=200)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='scheduled')
    visit_date = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")

    # Location
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_description = models.CharField(max_length=200, null=True, blank=True)

    # Content (from Kaduna)
    topics_discussed = models.JSONField(default=list, blank=True)
    observations = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    action_items = models.JSONField(default=list, blank=True)

    # Business assessment (from Kaduna)
    business_status = models.CharField(max_length=20, choices=BUSINESS_STATUS_CHOICES, null=True, blank=True)
    income_estimate = models.FloatField(null=True, blank=True, help_text="Estimated monthly income")
    challenges_faced = models.TextField(blank=True)
    support_needed = models.TextField(blank=True)

    # Evidence
    photo_urls = models.JSONField(default=list, blank=True)

    # Legacy field
    notes = models.TextField(blank=True)

    # Status
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.visit_id} - {self.name} - {self.household.name}"

    def save(self, *args, **kwargs):
        if not self.visit_id:
            # Generate visit ID: VIS-YYYY-NNNNN
            from datetime import datetime
            year = datetime.now().year
            last_visit = MentoringVisit.objects.filter(
                visit_id__startswith=f'VIS-{year}-'
            ).order_by('-created_at').first()

            if last_visit:
                last_num = int(last_visit.visit_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.visit_id = f'VIS-{year}-{new_num:05d}'

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'upg_mentoring_visits'
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['visit_date']),
            models.Index(fields=['household']),
            models.Index(fields=['mentor']),
            models.Index(fields=['completed']),
        ]


class PhoneNudge(models.Model):
    """
    Phone nudges/calls made by mentors to households
    """
    NUDGE_TYPE_CHOICES = [
        ('reminder', 'Training Reminder'),
        ('follow_up', 'Follow-up Call'),
        ('support', 'Support Call'),
        ('check_in', 'Regular Check-in'),
        ('business_advice', 'Business Advice'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='phone_nudges')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    nudge_type = models.CharField(max_length=20, choices=NUDGE_TYPE_CHOICES)
    call_date = models.DateTimeField()
    duration_minutes = models.IntegerField(help_text="Call duration in minutes")
    notes = models.TextField(blank=True)
    successful_contact = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_nudge_type_display()} - {self.household.name}"

    class Meta:
        db_table = 'upg_phone_nudges'


class MentoringReport(models.Model):
    """
    Weekly/Monthly mentoring reports by mentors
    """
    REPORTING_PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]

    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    reporting_period = models.CharField(max_length=20, choices=REPORTING_PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()

    # Summary statistics
    households_visited = models.IntegerField(default=0)
    phone_nudges_made = models.IntegerField(default=0)
    trainings_conducted = models.IntegerField(default=0)
    new_households_enrolled = models.IntegerField(default=0)

    # Narrative report
    key_activities = models.TextField(help_text="Key activities during the period")
    challenges_faced = models.TextField(blank=True)
    successes_achieved = models.TextField(blank=True)
    next_period_plans = models.TextField(blank=True)

    submitted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.get_full_name()} - {self.reporting_period} - {self.period_start}"

    class Meta:
        db_table = 'upg_mentoring_reports'
        unique_together = ['mentor', 'reporting_period', 'period_start']


class HouseholdTrainingEnrollment(models.Model):
    """
    Tracks household enrollment in trainings (one household per training rule)
    """
    household = models.OneToOneField(Household, on_delete=models.CASCADE, related_name='current_training_enrollment')
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='enrolled_households')
    enrolled_date = models.DateField()
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('enrolled', 'Enrolled'),
            ('completed', 'Completed'),
            ('dropped_out', 'Dropped Out'),
            ('transferred', 'Transferred'),
        ],
        default='enrolled'
    )
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.training.name}"

    class Meta:
        db_table = 'upg_household_training_enrollments'


class TrainingFieldAssociate(models.Model):
    """
    Assignment of training to Field Associates
    Creator (PM/M&E) assigns FA who then assigns mentors
    """
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending - Awaiting Mentor Assignment'),
        ('assigned', 'Assigned - Mentors Added'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='field_associates')
    field_associate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_fa_assignments',
                                        limit_choices_to={'role': 'field_associate'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='training_fa_assignments_made')

    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.training.name} -> FA: {self.field_associate.get_full_name()}"

    @property
    def mentor_count(self):
        return self.mentor_assignments.count()

    class Meta:
        db_table = 'upg_training_field_associates'
        unique_together = ['training', 'field_associate']


class TrainingMentorAssignment(models.Model):
    """
    Assignment of training to Mentors via Field Associate
    FA assigns mentors under them to the training
    """
    training_fa = models.ForeignKey(TrainingFieldAssociate, on_delete=models.CASCADE, related_name='mentor_assignments')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_mentor_assignments',
                              limit_choices_to={'role': 'mentor'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='training_mentor_assignments_made')

    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.training_fa.training.name} -> Mentor: {self.mentor.get_full_name()}"

    class Meta:
        db_table = 'upg_training_mentor_assignments'
        unique_together = ['training_fa', 'mentor']