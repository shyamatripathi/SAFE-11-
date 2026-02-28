from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user_email, username):

    subject = "Welcome to SAFE - Your Health Monitoring System"

    message = f"""
Hello {username},

Welcome to SAFE.

Your account has been successfully created.

We will monitor your health severity level and send reminders accordingly.

You can log in anytime to view your dashboard and speak with the SAFE AI assistant.

Stay proactive.
— SAFE System
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
    
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

