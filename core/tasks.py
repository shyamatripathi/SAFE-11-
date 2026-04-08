from django.utils import timezone
from datetime import timedelta
from core.email_engine import send_emergency_email
from .models import HealthProfile
from .email_engine import send_severity_email
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from celery import shared_task

@shared_task
def send_health_reminders():
    now = timezone.now()

    for health in HealthProfile.objects.select_related("user"):

        severity = health.severity
        last = health.last_email_sent

        should_send = False

        if severity == "High":
            should_send = not last or (now - last) >= timedelta(days=3)

        elif severity == "Moderate":
            should_send = not last or (now - last) >= timedelta(days=7)

        elif severity == "Low":
            should_send = not last or (now - last) >= timedelta(days=14)

        if should_send:
            print(f"[CELERY] Sending email to {health.user.email}")

            send_severity_email(health.user.email, severity)

            health.last_email_sent = now
            health.save()

@shared_task
def send_emergency_alert(user_id):

    user = User.objects.get(id=user_id)

    send_emergency_email(user.email, user.username)