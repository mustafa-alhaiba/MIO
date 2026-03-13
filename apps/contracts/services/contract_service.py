from datetime import date

from django.db import transaction
from django.db.models import QuerySet

from apps.contracts import models
from apps.common import file_validator
from apps.accounts.models import User

ROLES = User.Role

class ContractService:

    @staticmethod
    def get_queryset_for_user(user) -> QuerySet[models.Contract]:
        qs = models.Contract.objects.select_related("created_by").prefetch_related("parties")

        if user.role == ROLES.ADMIN:
            return qs
        elif user.role == ROLES.LAWYER:
            return qs.filter(created_by=user)
        return qs.filter(parties=user)

    @staticmethod
    def apply_filters(qs: QuerySet[models.Contract], params: dict) -> QuerySet[models.Contract]:
        status = params.get("status")
        if status:
            qs = qs.filter(status=status.upper())

        deadline_before = params.get("deadline_before")
        if deadline_before:
            qs = qs.filter(deadline__lte=deadline_before)

        deadline_after = params.get("deadline_after")
        if deadline_after:
            qs = qs.filter(deadline__gte=deadline_after)

        return qs

    @staticmethod
    @transaction.atomic
    def create_contract(validated_data: dict, created_by) -> models.Contract:
        parties = validated_data.pop("parties", [])

        contract = models.Contract(created_by=created_by, **validated_data)
        contract.sync_expired_status()      
        contract.full_clean()               
        contract.save()

        if parties:
            contract.parties.set(parties)

        return contract

    @staticmethod
    @transaction.atomic
    def update_contract(contract: models.Contract, validated_data: dict) -> models.Contract:
        parties = validated_data.pop("parties", None)

        for attr, value in validated_data.items():
            setattr(contract, attr, value)

        contract.sync_expired_status()
        contract.full_clean()
        contract.save()

        if parties is not None:
            contract.parties.set(parties)

        return contract

    @staticmethod
    @transaction.atomic
    def attach_document(contract: models.Contract, file_obj) -> models.Contract:
        file_validator.validate_contract_document(file_obj)

        if contract.document:
            contract.document.delete(save=False)

        contract.document = file_obj
        contract.save(update_fields=["document", "updated_at"])
        return contract

    @staticmethod
    def soft_delete_contract(contract: models.Contract) -> None:
        contract.soft_delete()

    @staticmethod
    def expire_overdue_contracts() -> int:
        overdue = models.Contract.objects.filter(
            deadline__lt=date.today(),
            status=models.Contract.Status.ACTIVE,
        )
        count = overdue.count()
        overdue.update(status=models.Contract.Status.EXPIRED)
        return count