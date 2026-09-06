from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = "Створює/оновлює periodic tasks для Celery Beat"

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(minute="*/2", hour="*")
        task, created = PeriodicTask.objects.update_or_create(
            name="Очищення сесій щоночі",
            defaults={
                "crontab": schedule,
                "task": "user_management.tasks.cleanup_sessions",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Periodic task створено"))
        else:
            self.stdout.write(self.style.SUCCESS("Periodic task оновлено"))