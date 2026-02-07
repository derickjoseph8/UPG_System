from django.contrib import admin
from .models import (
    TargetingRuleGroup, TargetingRule, EnrollmentApplication, Verification
)


@admin.register(TargetingRuleGroup)
class TargetingRuleGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'logic_operator', 'priority', 'is_mandatory', 'is_active']
    list_filter = ['program', 'logic_operator', 'is_mandatory', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['priority', 'name']


@admin.register(TargetingRule)
class TargetingRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'rule_type', 'operator', 'priority', 'is_mandatory', 'is_active']
    list_filter = ['category', 'operator', 'is_mandatory', 'is_active', 'program']
    search_fields = ['name', 'description', 'rule_type']
    ordering = ['priority', 'name']


@admin.register(EnrollmentApplication)
class EnrollmentApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_id', 'get_full_name', 'id_number', 'phone_number', 'status', 'village', 'created_at']
    list_filter = ['status', 'program', 'village', 'approved', 'screening_passed']
    search_fields = ['application_id', 'first_name', 'last_name', 'id_number', 'phone_number']
    readonly_fields = ['application_id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Application Info', {
            'fields': ('application_id', 'status', 'current_step', 'program')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'id_number', 'phone_number', 'village')
        }),
        ('Application Data', {
            'fields': ('application_data',)
        }),
        ('Screening', {
            'fields': ('screening_score', 'screening_passed', 'screening_date', 'screening_notes')
        }),
        ('Validation', {
            'fields': ('id_validated', 'id_validation_date', 'phone_validated', 'phone_validation_date')
        }),
        ('Poverty Assessment', {
            'fields': ('poverty_score', 'poverty_score_fetched_date')
        }),
        ('Approval', {
            'fields': ('approved', 'approved_by', 'approved_date', 'rejection_reason')
        }),
        ('Enrollment', {
            'fields': ('household',)
        }),
        ('Metadata', {
            'fields': ('submitted_by', 'created_at', 'updated_at')
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['application', 'verification_type', 'status', 'verified_by', 'verification_date']
    list_filter = ['status', 'verification_type']
    search_fields = ['application__application_id', 'application__first_name', 'application__last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
