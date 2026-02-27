from django.shortcuts import render
from .email_engine import send_severity_email

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, HealthProfileForm
from .models import HealthProfile

def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        profile_form = HealthProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            send_severity_email(user.email, profile.severity)

            login(request, user)
            return redirect("dashboard")

    else:
        user_form = UserRegistrationForm()
        profile_form = HealthProfileForm()

    return render(request, "register.html", {
        "user_form": user_form,
        "profile_form": profile_form
    })


from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    profile = HealthProfile.objects.get(user=request.user)
    chatbot_response = None

    if request.method == "POST":
        message = request.POST.get("chat_message", "")
        chatbot_response = generate_chatbot_response(message)

    return render(request, "dashboard.html", {
        "profile": profile,
        "chatbot_response": chatbot_response
    })


def generate_chatbot_response(message):
    message = message.lower()

    # Empathy
    if "scared" in message or "worried" in message:
        empathy = "I understand this may feel worrying. Let's assess it calmly. "
    elif "pain" in message:
        empathy = "I'm sorry you're experiencing discomfort. "
    else:
        empathy = "Thank you for sharing. "

    # Doctor Suggestion
    if "chest pain" in message:
        doctor = "You should consult a Cardiologist immediately."
    elif "stomach" in message:
        doctor = "It would be helpful to see a Gastroenterologist."
    elif "anxiety" in message:
        doctor = "Consider speaking with a Psychiatrist or Clinical Psychologist."
    elif "headache" in message:
        doctor = "A Neurologist may help if symptoms persist."
    else:
        doctor = "If symptoms continue, consider visiting a General Physician."

    return empathy + doctor