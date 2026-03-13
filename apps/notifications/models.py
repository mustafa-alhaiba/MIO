from django.db import models
from django.contrib.auth import get_user_model

from apps.contracts.models import Contract

User = get_user_model()


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"], name="idx_notif_recipient_read"),
        ]

    def __str__(self):
        return f"Notification({self.recipient_id}, contract={self.contract_id}, read={self.is_read})"
