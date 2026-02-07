"""
Django Signals for KoboToolbox Auto-Sync
Automatically trigger form sync when forms are activated or assigned
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from .models import FormTemplate, FormAssignment
from .kobo_service import sync_form_to_kobo


# Store previous status to detect changes
_form_template_previous_status = {}


@receiver(pre_save, sender=FormTemplate)
def store_previous_status(sender, instance, **kwargs):
    """
    Store the previous status before save to detect status changes

    Args:
        sender: FormTemplate model class
        instance: FormTemplate instance being saved
    """
    if instance.pk:
        try:
            old_instance = FormTemplate.objects.get(pk=instance.pk)
            _form_template_previous_status[instance.pk] = old_instance.status
        except FormTemplate.DoesNotExist:
            pass


@receiver(post_save, sender=FormTemplate)
def auto_sync_on_activation(sender, instance, created, **kwargs):
    """
    Trigger sync when FormTemplate status changes to Active

    Conditions for syncing:
    - sync_to_kobo must be True
    - status must be 'active'
    - Status must have changed to 'active' (not already active)
    - KOBO_AUTO_SYNC_ON_ACTIVATION setting must be True

    Args:
        sender: FormTemplate model class
        instance: FormTemplate instance that was saved
        created: Boolean indicating if this is a new instance
    """
    # Check if auto-sync is enabled in settings
    auto_sync_enabled = getattr(settings, 'KOBO_AUTO_SYNC_ON_ACTIVATION', True)
    if not auto_sync_enabled:
        return

    # Only sync if sync_to_kobo is enabled
    if not instance.sync_to_kobo:
        return

    # Only sync if status is active
    if instance.status != 'active':
        return

    # Check if status changed to active (not already active)
    previous_status = _form_template_previous_status.get(instance.pk)

    # Sync if:
    # 1. This is a new instance (created=True) and status is active
    # 2. Status changed from non-active to active
    should_sync = (
        (created and instance.status == 'active') or
        (previous_status and previous_status != 'active' and instance.status == 'active')
    )

    if should_sync:
        # Trigger sync (run synchronously for now)
        try:
            sync_form_to_kobo(instance, user=instance.created_by)
        except Exception as e:
            # Log error but don't raise exception to avoid blocking form save
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Auto-sync failed for form {instance.id}: {str(e)}")

    # Clean up stored status
    if instance.pk in _form_template_previous_status:
        del _form_template_previous_status[instance.pk]


@receiver(post_save, sender=FormAssignment)
def sync_on_assignment(sender, instance, created, **kwargs):
    """
    Trigger sync when form is assigned to mentor/field associate

    Conditions for syncing:
    - This must be a new assignment (created=True)
    - form_template.sync_to_kobo must be True
    - KOBO_AUTO_SYNC_ON_ASSIGNMENT setting must be True
    - Form should be synced if not already synced or if outdated

    Args:
        sender: FormAssignment model class
        instance: FormAssignment instance that was saved
        created: Boolean indicating if this is a new instance
    """
    # Only sync on new assignments
    if not created:
        return

    # Check if auto-sync is enabled in settings
    auto_sync_enabled = getattr(settings, 'KOBO_AUTO_SYNC_ON_ASSIGNMENT', True)
    if not auto_sync_enabled:
        return

    # Only sync if sync_to_kobo is enabled for this form
    if not instance.form_template.sync_to_kobo:
        return

    # Check if form needs sync
    form = instance.form_template
    needs_sync = (
        form.kobo_sync_status in ['never_synced', 'sync_failed', 'sync_outdated'] or
        not form.kobo_asset_uid
    )

    if needs_sync:
        # Trigger sync
        try:
            sync_form_to_kobo(form, user=instance.assigned_by)
        except Exception as e:
            # Log error but don't raise exception
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Auto-sync on assignment failed for form {form.id}: {str(e)}")
