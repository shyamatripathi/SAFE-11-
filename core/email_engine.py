from django.core.mail import send_mail
from django.conf import settings

def send_severity_email(user_email, severity):

    if severity == "High":
        timeline = "You should consult a doctor within 1 week or sooner."
        frequency = "You will receive daily reminders."
    elif severity == "Moderate":
        timeline = "Consult a doctor within 2 weeks."
        frequency = "You will receive reminders twice a week."
    else:
        timeline = "Monitor condition and consult within 3–4 weeks if needed."
        frequency = "You will receive weekly reminders."

    subject = "SAFE Health Risk Assessment"
    message = f"""
Your severity level: {severity}

{timeline}

{frequency}

Please take appropriate action.

— SAFE System
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )