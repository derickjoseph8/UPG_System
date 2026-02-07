"""
Business Savings Groups (BSG) Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from households.models import Household
from business_groups.models import BusinessGroup

User = get_user_model()


class BusinessSavingsGroup(models.Model):
    """
    Community-based savings entity for entrepreneurs
    Can include multiple business groups and individual households
    """
    SAVINGS_FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]

    name = models.CharField(max_length=100)
    business_groups = models.ManyToManyField(BusinessGroup, blank=True, related_name='savings_groups', help_text="Business groups that are part of this savings group")
    members_count = models.IntegerField(default=0)
    target_members = models.IntegerField(default=25, help_text="Target number of members for this savings group")
    savings_to_date = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    formation_date = models.DateField()
    meeting_day = models.CharField(max_length=20, blank=True)
    meeting_location = models.CharField(max_length=100, blank=True)
    savings_frequency = models.CharField(max_length=20, choices=SAVINGS_FREQUENCY_CHOICES, default='weekly', help_text="How often members save")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_savings_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_members(self):
        """Get total count of individual members plus business group members"""
        individual_members = self.bsg_members.filter(is_active=True).count()
        bg_members = sum([bg.members.count() for bg in self.business_groups.all()])
        return individual_members + bg_members

    class Meta:
        db_table = 'upg_business_savings_groups'


class BSGMember(models.Model):
    """
    BSG membership tracking
    """
    ROLE_CHOICES = [
        ('chairperson', 'Chairperson'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('member', 'Member'),
    ]

    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='bsg_members')
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_date = models.DateField()
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.household.name} - {self.bsg.name}"

    class Meta:
        db_table = 'upg_bsg_members'
        unique_together = ['bsg', 'household']  # Prevent duplicate memberships
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]


class BSGProgressSurvey(models.Model):
    """
    Monthly BSG performance tracking
    """
    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='progress_surveys')
    survey_date = models.DateField()
    saving_last_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month_recorded = models.DateField()
    attendance_this_meeting = models.IntegerField(default=0)
    surveyor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bsg.name} - {self.month_recorded}"

    class Meta:
        db_table = 'upg_bsg_progress_surveys'


class SavingsRecord(models.Model):
    """
    Individual savings record for BSG members
    """
    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='savings_records')
    member = models.ForeignKey(BSGMember, on_delete=models.CASCADE, related_name='savings_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    savings_date = models.DateField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_savings')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Edit tracking fields
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_savings')
    edited_at = models.DateTimeField(null=True, blank=True)
    edit_history = models.TextField(blank=True, help_text="History of all edits made to this record")

    def __str__(self):
        return f"{self.member.household.name} - KES {self.amount} on {self.savings_date}"

    class Meta:
        db_table = 'upg_savings_records'
        ordering = ['-savings_date', '-created_at']


class BSGLoan(models.Model):
    """
    Loan record for BSG members borrowing from the group's savings pool.
    This is a recording system - mentors record loans as they are issued by the group.
    """
    LOAN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('partially_repaid', 'Partially Repaid'),
        ('fully_repaid', 'Fully Repaid'),
        ('defaulted', 'Defaulted'),
    ]

    bsg = models.ForeignKey(BusinessSavingsGroup, on_delete=models.CASCADE, related_name='loans')
    member = models.ForeignKey(BSGMember, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount borrowed")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Interest rate in percentage")
    total_due = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Principal + Interest")
    amount_repaid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    loan_date = models.DateField(help_text="Date loan was issued")
    due_date = models.DateField(help_text="Date loan should be fully repaid")
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='active')

    purpose = models.TextField(blank=True, help_text="Reason for taking the loan")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_bsg_loans')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate total due (principal + interest) if not set
        if not self.total_due or self.total_due == 0:
            interest = self.loan_amount * (self.interest_rate / 100)
            self.total_due = self.loan_amount + interest
        # Calculate balance
        self.balance = self.total_due - self.amount_repaid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan: {self.member.household} - KES {self.loan_amount} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status in ['active', 'partially_repaid'] and self.due_date < timezone.now().date()

    @property
    def repayment_percentage(self):
        if self.total_due > 0:
            return round((self.amount_repaid / self.total_due) * 100, 1)
        return 0

    class Meta:
        db_table = 'upg_bsg_loans'
        ordering = ['-loan_date', '-created_at']


class LoanRepayment(models.Model):
    """
    Individual repayment record for a BSG loan
    """
    loan = models.ForeignKey(BSGLoan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_date = models.DateField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the loan's amount_repaid and status
        loan = self.loan
        total_repaid = loan.repayments.aggregate(total=models.Sum('amount'))['total'] or 0
        loan.amount_repaid = total_repaid
        loan.balance = loan.total_due - total_repaid

        if loan.balance <= 0:
            loan.status = 'fully_repaid'
        elif total_repaid > 0:
            loan.status = 'partially_repaid'
        loan.save()

    def __str__(self):
        return f"Repayment: KES {self.amount} on {self.repayment_date} for {self.loan}"

    class Meta:
        db_table = 'upg_loan_repayments'
        ordering = ['-repayment_date', '-created_at']