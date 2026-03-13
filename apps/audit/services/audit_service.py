from apps.audit.models import AuditLog

TRACKED_FIELDS = ["title", "arabic_title", "description", "status", "deadline", "document"]


class ContractAuditService:

    @staticmethod
    def audit_create(contract, user=None) -> AuditLog:
        return AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.CREATE,
            contract=contract,
            contract_title=contract.title,
            extra_data={"status": contract.status, "deadline": str(contract.deadline)},
        )

    @staticmethod
    def audit_update(contract, user=None, changed_fields: dict | None = None) -> AuditLog:
        return AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.UPDATE,
            contract=contract,
            contract_title=contract.title,
            extra_data={"changed_fields": changed_fields or {}},
        )

    @staticmethod
    def audit_soft_delete(contract, user=None) -> AuditLog:
        return AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.SOFT_DELETE,
            contract=contract,
            contract_title=contract.title,
            extra_data={"deleted_at": str(contract.deleted_at)},
        )

    @staticmethod
    def audit_restore(contract, user=None) -> AuditLog:
        return AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.RESTORE,
            contract=contract,
            contract_title=contract.title,
            extra_data={},
        )

    @staticmethod
    def audit_delete(contract, user=None) -> AuditLog:
        return AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.DELETE,
            contract=None,
            contract_title=contract.title,
            extra_data={"contract_id": str(contract.pk), "title": contract.title},
        )
