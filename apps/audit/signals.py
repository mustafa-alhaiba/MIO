from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.audit.services.audit_service import ContractAuditService, TRACKED_FIELDS
from apps.common.context import get_current_user
from apps.contracts.models import Contract


@receiver(pre_save, sender=Contract)
def snapshot_contract_before_save(sender, instance, **kwargs):
    if not instance.pk:
        instance._pre_save_snapshot = None
        return
    try:
        instance._pre_save_snapshot = Contract.all_objects.get(pk=instance.pk)
    except Contract.DoesNotExist:
        instance._pre_save_snapshot = None


@receiver(post_save, sender=Contract)
def on_contract_saved(sender, instance, created, **kwargs):
    user = get_current_user()

    if created:
        ContractAuditService.audit_create(instance, user)
        return

    old = getattr(instance, "_pre_save_snapshot", None)
    if old is None:
        return

    if old.deleted_at is None and instance.deleted_at is not None:
        ContractAuditService.audit_soft_delete(instance, user)
        return

    if old.deleted_at is not None and instance.deleted_at is None:
        ContractAuditService.audit_restore(instance, user)
        return

    changed = {
        field: {"from": str(getattr(old, field)), "to": str(getattr(instance, field))}
        for field in TRACKED_FIELDS
        if str(getattr(old, field, "")) != str(getattr(instance, field, ""))
    }
    if changed:
        ContractAuditService.audit_update(instance, user, changed)


@receiver(post_delete, sender=Contract)
def on_contract_hard_deleted(sender, instance, **kwargs):
    ContractAuditService.audit_delete(instance, get_current_user())
