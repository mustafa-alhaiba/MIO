import logging

from celery import shared_task

from apps.notifications.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


@shared_task(name="notifications.check_upcoming_deadlines")
def check_upcoming_deadlines():
    result = NotificationService.create_deadline_notifications()
    logger.info(
        "check_upcoming_deadlines: %d notifications created for %d contracts.",
        result["notifications_created"],
        result["contracts_checked"],
    )
    return result
