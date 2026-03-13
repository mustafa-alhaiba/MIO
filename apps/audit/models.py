from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AuditLog(models.Model):

    class Action(models.TextChoices):
        CREATE      = "CREATE",      _("Create")
        UPDATE      = "UPDATE",      _("Update")
        DELETE      = "DELETE",      _("Hard Delete")
        SOFT_DELETE = "SOFT_DELETE", _("Soft Delete")
        RESTORE     = "RESTORE",     _("Restore")

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices, db_index=True)

    contract = models.ForeignKey(
        "contracts.Contract",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    # Snapshot of the title so we can display it even after hard delete
    contract_title = models.CharField(max_length=255, blank=True)

    timestamp  = models.DateTimeField(auto_now_add=True, db_index=True)
    extra_data = models.JSONField(default=dict)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["contract", "action"], name="idx_audit_contract_action"),
            models.Index(fields=["user", "action"],     name="idx_audit_user_action"),
        ]

    def __str__(self):
        return f"AuditLog({self.action}, contract={self.contract_title}, user={self.user_id})"
