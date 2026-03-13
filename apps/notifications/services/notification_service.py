from ast import List
from apps.contracts.models import Contract
from apps.notifications.models import Notification


class NotificationService:

    @staticmethod
    def create_deadline_notifications() -> dict:
        contracts = (
            Contract.objects.expiring_soon(days=7)
            .select_related("created_by")
            .prefetch_related("parties")
        )

        candidates: list[tuple[int, object]] = []
        messages: dict[object, str] = {}

        for contract in contracts:
            recipients = {contract.created_by} | set(contract.parties.all())
            message = (
                f"Contract '{contract.title}' is approaching its deadline on "
                f"{contract.deadline}. Please take action before the deadline."
            )
            messages[contract.pk] = message
            for user in recipients:
                candidates.append((user.pk, contract.pk))

        if not candidates:
            return {"contracts_checked": 0, "notifications_created": 0}

        existing = set(
            Notification.objects.filter(
                is_read=False,
                recipient_id__in={uid for uid, _ in candidates},
                contract_id__in={cid for _, cid in candidates},
            ).values_list("recipient_id", "contract_id")
        )

        to_create = [
            Notification(
                recipient_id=uid,
                contract_id=cid,
                message=messages[cid],
            )
            for uid, cid in candidates
            if (uid, cid) not in existing
        ]

        notifications = Notification.objects.bulk_create(to_create)
        #after creating we send the notifications
        #NotificationService.send_notification(notifications) 
        return {
            "contracts_checked": contracts.count(),
            "notifications_created": len(to_create),
        }


    @staticmethod
    def send_notification(notifications) -> None:
        #call the service that handle send notificiaton
        #somthing like : SenderService.send_notification.delay(notifications_ids)
        return None