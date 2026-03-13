from django.db import models
from apps.contracts import queryset

class ContractManager(models.Manager):
    def get_queryset(self):
        return queryset.ContractQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        return queryset.ContractQuerySet(self.model, using=self._db)
