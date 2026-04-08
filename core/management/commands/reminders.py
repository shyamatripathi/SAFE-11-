from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import HealthProfile
from core.email_engine import send_severity_email


class Command(BaseCommand):
    help = "Send periodic health reminder emails"

    def handle(self, *args, **kwargs):

        now = timezone.now()

        for profile in HealthProfile.objects.select_related("user"):

            severity = profile.severity
            last = getattr(profile, "last_email_sent", None)

            should_send = False

            if severity == "High":
                should_send = not last or (now - last) >= timedelta(days=3)

            elif severity == "Moderate":
                should_send = not last or (now - last) >= timedelta(days=7)

            elif severity == "Low":
                should_send = not last or (now - last) >= timedelta(days=14)

            if should_send:
                print(f"[CRON] Sending email to {profile.user.email}")

                send_severity_email(profile.user.email, severity)

                profile.last_email_sent = now
                profile.save()