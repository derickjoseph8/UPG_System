"""
VE Reporting Admin Configuration
Allows MIS admins to manage VE API keys through Django admin.
"""
from django.contrib import admin
from .models import VEApiKey


@admin.register(VEApiKey)
class VEApiKeyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'key_prefix', 'is_active', 'created_at',
        'expires_at', 'last_used_at', 'created_by'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['name', 'key_prefix']
    readonly_fields = [
        'uuid', 'key_hash', 'key_prefix', 'created_at', 'updated_at',
        'last_used_at', 'last_used_ip', 'revoked_at', 'revoked_by'
    ]
    ordering = ['-created_at']

    fieldsets = (
        ('Key Information', {
            'fields': ('name', 'key_prefix', 'uuid')
        }),
        ('Permissions', {
            'fields': ('scopes', 'rate_limit_per_minute')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Usage', {
            'fields': ('last_used_at', 'last_used_ip'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Revocation', {
            'fields': ('revoked_at', 'revoked_by', 'revoke_reason'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            # New key - set created_by
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
