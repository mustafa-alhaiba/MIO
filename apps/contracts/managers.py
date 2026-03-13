from django.db import models
from apps.contracts import queryset

class ContractManager(models.Manager):
    def get_queryset(self):
        return queryset.ContractQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        return queryset.ContractQuerySet(self.model, using=self._db)

    def expiring_soon(self, days: int = 7):
        return self.get_queryset().expiring_soon(days=days)