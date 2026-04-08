from django.shortcuts import render
from .email_engine import send_welcome_email, send_severity_email
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, HealthProfileForm
from .models import HealthProfile
from .forms import HealthUpdateForm#added later for update health form
from django.contrib.auth.decorators import login_required
from .safe_chatbot import safe_chatbot
from django.http import JsonResponse
import json


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
            # Join the list of selected symptoms into a comma-separated string
            symptoms_list = profile_form.cleaned_data.get('symptoms', [])
            profile.symptoms = ', '.join(symptoms_list)
            profile.save()
            send_welcome_email(user.email, user.username)
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




@login_required
def dashboard(request):

    profile = HealthProfile.objects.get(user=request.user)

    chatbot_response = None

    if request.method == "POST":

        message = request.POST.get("chat_message")

        if message:
            chatbot_response = safe_chatbot(
                user_id=request.user.id,
                user_message=message,
                severity=profile.severity,
                symptoms=profile.symptoms,
                bmi=profile.bmi,
                age=profile.age
            )
            print(f"Chatbot response: {chatbot_response}")    

    # symptoms list for UI
    symptom_list = []
    if profile.symptoms:
        symptom_list = [s.strip() for s in profile.symptoms.split(",")]

    return render(request, "dashboard.html", {
        "profile": profile,
        "chatbot_response": chatbot_response,
        "symptom_list": symptom_list
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
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("login")
@login_required
def update_health(request):

    user = request.user
    profile = HealthProfile.objects.get(user=user)

    if request.method == "POST":
        user_form = HealthUpdateForm(request.POST, instance=user)
        profile_form = HealthUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("dashboard")

    else:
        user_form = HealthUpdateForm(instance=user)
        profile_form = HealthUpdateForm(instance=profile)

    return render(request, "update_health.html", {
        "user_form": user_form,
        "profile_form": profile_form
    })

def chat_api(request):
    data = json.loads(request.body)

    reply = safe_chatbot(
        user_id=request.user.id,
        user_message=data["message"],
        severity=data["severity"],
        symptoms=data["symptoms"],
        bmi=data["bmi"],
        age=data["age"]
    )

    return JsonResponse({"response": reply})