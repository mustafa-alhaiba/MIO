import uuid
import os
from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.contracts import managers
from apps.common import file_validator

User = get_user_model()

def contract_document_upload_path(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return f"contracts/{instance.pk}/documents/{uuid.uuid4().hex}{ext}"

class Contract(models.Model):

    class Status(models.TextChoices):
        DRAFT    = "DRAFT",    _("Draft")
        ACTIVE   = "ACTIVE",   _("Active")
        EXPIRED  = "EXPIRED",  _("Expired")
        ARCHIVED = "ARCHIVED", _("Archived")

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title       = models.CharField(max_length=255)

    arabic_title = models.CharField(max_length=255, blank=True, default="")

    description = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=100,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,          
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_contracts",
        db_index=True,
    )
    parties = models.ManyToManyField(
        User,
        related_name="contracts_as_party",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deadline = models.DateField(db_index=True)

    document = models.FileField(
        upload_to=contract_document_upload_path,
        blank=True,
        null=True,
        validators=[file_validator.validate_contract_document],
    )

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects       = managers.ContractManager()   
    all_objects   = models.Manager()    

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "deadline"], name="idx_contract_status_deadline"),
            models.Index(fields=["created_by", "status"],  name="idx_contract_creator_status"),
        ]

    def __str__(self):
        return f"{self.title} [{self.status}]"

    @property
    def is_expired(self) -> bool:
        return (
            self.deadline < date.today()
        )

    def sync_expired_status(self) -> bool:
        if self.is_expired:
            self.status = self.Status.EXPIRED
            return True
        return False

    def soft_delete(self, commit: bool = True) -> None:
        self.deleted_at = timezone.now()
        if commit:
            self.save(update_fields=["deleted_at", "updated_at"])

    def restore(self, commit: bool = True) -> None:
        self.deleted_at = None
        if commit:
            self.save(update_fields=["deleted_at", "updated_at"])