from django import forms
from django.contrib.auth.models import User
from .models import HealthProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class HealthProfileForm(forms.ModelForm):
    class Meta:
        model = HealthProfile
        fields = ['age', 'height', 'weight', 'symptoms', 'heart_history']