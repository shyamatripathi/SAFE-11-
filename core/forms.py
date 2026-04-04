from django import forms
from django.contrib.auth.models import User
from .models import HealthProfile

SYMPTOM_CHOICES = [
    ('chest pain', 'Chest Pain'),
    ('shortness of breath', 'Shortness of Breath'),
    ('fever', 'Fever'),
    ('cough', 'Cough'),
    ('cold', 'Cold'),
    ('headache', 'Headache'),
    ('nausea', 'Nausea'),
    ('dizziness', 'Dizziness'),
    ('fatigue', 'Fatigue'),
    ('vomiting', 'Vomiting'),
]


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class HealthProfileForm(forms.ModelForm):
    symptoms = forms.MultipleChoiceField(
        choices=SYMPTOM_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,#changed from True to False to allow users to submit the form without selecting any symptoms
        help_text='Select all symptoms that apply',
    )

    class Meta:
        model = HealthProfile
        fields = ['age', 'height', 'weight', 'symptoms', 'heart_history']

class HealthUpdateForm(forms.ModelForm):
    class Meta:
        model = HealthProfile
        fields = ['age', 'height', 'weight', 'symptoms', 'heart_history']