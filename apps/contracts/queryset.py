from django.db import models
from datetime import date
from apps.contracts import models as contract_models

class ContractQuerySet(models.QuerySet):
    def active(self):
        
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def expiring_soon(self, days: int = 7):
        from datetime import timedelta
        today = date.today()
        cutoff = today + timedelta(days=days)
        return self.active().filter(
            status=contract_models.Contract.Status.ACTIVE,
            deadline__gte=today,
            deadline__lte=cutoff,
        )
