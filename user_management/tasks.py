from celery import shared_task
from django.contrib.sessions.models import Session
from django.utils import timezone

@shared_task(ignore_result=True)
def cleanup_sessions():
    Session.objects.filter(expire_date__lt=timezone.now()).delete()