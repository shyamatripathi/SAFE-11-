from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user_email, username):

    subject = "Welcome to SAFE - Your Health Monitoring System"

    plain_message = f"""
Hello {username},

Welcome to SAFE.

Your account has been successfully created.
We will monitor your health severity level and send reminders accordingly.
You can log in anytime to view your dashboard and speak with the SAFE AI assistant.

Stay proactive.
— SAFE System

Reply to this email to delete your SAFE account.
"""

    html_message = f"""
    <p>Hello {username},</p>

    <p>Welcome to <strong>SAFE</strong>.</p>

    <p>Your account has been successfully created.</p>
    </p>We will monitor your health severity level and send reminders accordingly.</p>
    </p>You can log in anytime to view your dashboard and speak with the SAFE AI assistant.</p>

    <p>Stay proactive.<br>
    — SAFE System</p>

    <p style="font-size:12px; color:gray;">
    Reply to this email to delete your SAFE account.
    </p>
    """

    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
        html_message=html_message
    )


def send_severity_email(user_email, severity):

    if severity == "High":
        timeline = "You should consult a doctor within 1 week or sooner."
        frequency = "You will receive daily reminders."
        color = "red"
    elif severity == "Moderate":
        timeline = "Consult a doctor within 2 weeks."
        frequency = "You will receive reminders twice a week."
        color = "orange"
    else:
        timeline = "Monitor condition and consult within 3–4 weeks if needed."
        frequency = "You will receive weekly reminders."
        color = "green"

    subject = "SAFE Health Risk Assessment"

    plain_message = f"""
Your severity level: {severity}

{timeline}

{frequency}

Please take appropriate action.

— SAFE System
"""

    html_message = f"""
    <p>Your severity level:
    <strong style="color:{color};">{severity}</strong></p>

    <p>{timeline}</p>

    <p>{frequency}</p>

    <p>Please take appropriate action.</p>

    <p>— SAFE System</p>

    <p style="font-size:12px; color:gray;">
    This is an automated health risk reminder.
    </p>
    """

    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
        html_message=html_message
    )