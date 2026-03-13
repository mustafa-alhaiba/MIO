from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


TASK_NAME = "Daily: check upcoming contract deadlines"
TASK_PATH = "apps.notifications.tasks.check_upcoming_deadlines"


class Command(BaseCommand):
    help = "Register the check_upcoming_deadlines Celery Beat periodic task in the database."

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        task, created = PeriodicTask.objects.update_or_create(
            name=TASK_NAME,
            defaults={
                "task": TASK_PATH,
                "crontab": schedule,
                "enabled": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created periodic task: '{TASK_NAME}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated periodic task: '{TASK_NAME}'"))
