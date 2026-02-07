"""
VE API Key model for Village Enterprise reporting access
"""
import uuid
import secrets
import hashlib
from django.db import models
from django.utils import timezone


class VEApiKey(models.Model):
    """
    API Key for Village Enterprise to access reporting endpoints.
    Keys are scoped to only ve-reporting endpoints and are rate-limited.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=255, unique=True, db_index=True)
    key_prefix = models.CharField(max_length=12)  # First 12 chars for identification

    # Scopes and permissions
    scopes = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)

    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=100)

    # Timestamps
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.CharField(max_length=50, null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_ve_api_keys'
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_ve_api_keys'
    )
    revoke_reason = models.TextField(null=True, blank=True)

    # Standard fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 've_api_keys'
        verbose_name = 'VE API Key'
        verbose_name_plural = 'VE API Keys'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @staticmethod
    def generate_key():
        """
        Generate a new API key.
        Returns: (full_key, key_hash, key_prefix)
        """
        key = f"ve_live_{secrets.token_urlsafe(32)}"
        key_prefix = key[:12]
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash, key_prefix

    @staticmethod
    def hash_key(key):
        """Hash a key for comparison"""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify_key(self, key):
        """Verify if a key matches this record"""
        return self.key_hash == self.hash_key(key)

    def is_valid(self):
        """Check if the key is valid (active and not expired)"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.revoked_at:
            return False
        if self.is_deleted:
            return False
        return True

    def record_usage(self, ip_address=None):
        """Record that the key was used"""
        self.last_used_at = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.save(update_fields=['last_used_at', 'last_used_ip'])

    def save(self, *args, **kwargs):
        if not self.scopes:
            self.scopes = ["ve-reporting:read"]
        super().save(*args, **kwargs)
