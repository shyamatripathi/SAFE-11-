
from google import genai
import os
from .memory import get_memory_context, update_memory
from .tasks import send_emergency_alert
from .models import HealthProfile
from django.utils import timezone
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Configure API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def fallback_response(user_id, user_message, severity, symptoms):
    msg = (user_message or "").lower()

    # Emergency override
    #  EMERGENCY
    if "chest" in msg and "pain" in msg:

        profile = HealthProfile.objects.get(user_id=user_id)

        #  prevent spam (6-hour cooldown)
        if not profile.last_emergency_alert or \
           (timezone.now() - profile.last_emergency_alert).total_seconds() > 21600:

            send_emergency_alert.delay(user_id)

            profile.last_emergency_alert = timezone.now()
            profile.save()

        return "Chest pain can be serious. Please seek immediate medical attention."

    if "unconscious" in msg or "seizure" in msg:
        return "This could be a medical emergency. Seek immediate help."
    symptoms = (symptoms or "").lower()

    if "shortness of breath" in msg or "breathing" in msg:
        return "Difficulty in breathing can be serious. Please consult a doctor immediately."

    if "seizure" in msg or "unconscious" in msg:
        return "This could be a medical emergency. Seek immediate help."

    # USER MESSAGE FIRST (priority)
    if "stress" in msg or "anxiety" in msg:
        return "It sounds like you're feeling stressed. Try slowing down, taking deep breaths, and giving yourself a moment to reset."

    if "headache" in msg:
        return "Headaches are often caused by stress or dehydration. Try resting and staying hydrated."

    if "dizziness" in msg:
        return "Dizziness can be due to low blood pressure or dehydration. Sit down and hydrate."

    if "fatigue" in msg or "tired" in msg:
        return "Fatigue may be due to lack of rest or stress. Make sure you're getting enough sleep."

    if "cold" in msg or "cough" in msg:
        return "This looks like a mild cold. Stay hydrated and get enough rest."

    #  NOW use stored symptoms as CONTEXT 
    if "chest pain" in symptoms:
        return "You previously reported chest pain. If it's still present, consider seeing a doctor."

    #  Severity LAST
    if severity == "High":
        return "Your condition may need attention. Please consider consulting a doctor soon."

    if severity == "Moderate":
        return "Monitor your symptoms closely. If they persist, consult a doctor."

    if severity == "Mild":
        return "Your condition seems manageable. Maintain a healthy routine and observe symptoms."

    return "I'm here to help. Could you tell me more about what you're feeling?"


def safe_chatbot(user_id, user_message, severity, symptoms, bmi, age):    

    memory_context = get_memory_context(user_id)

    prompt = f"""
You are a health assistant AI.

You must:
- Respond based on the user's CURRENT message first
- Use past conversation as context (not override)
- Be empathetic, natural, and conversational
- Avoid repeating the same response every time
- Give helpful, human-like replies (not robotic)

User Profile:
- Risk Level: {severity}
- Known Symptoms: {symptoms}

Conversation History:
{memory_context}

User just said:
"{user_message}"

Now respond like a caring assistant:
"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        if response and response.text:
            bot_reply = response.text.strip()
        else:
            bot_reply = fallback_response(user_id, user_message, severity, symptoms)

    except Exception:
        bot_reply = fallback_response(user_id, user_message, severity, symptoms)

    update_memory(user_id, user_message, bot_reply)
    return bot_reply