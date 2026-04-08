from django.db import models
from django.contrib.auth.models import User
from .ml_model import predict_severity

class HealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    age = models.IntegerField()
    height = models.FloatField()  # in cm
    weight = models.FloatField()  # in kg
    bmi = models.FloatField(blank=True, null=True)

    symptoms = models.TextField()
    heart_history = models.BooleanField(default=False)

    severity = models.CharField(max_length=20, blank=True)
    last_emergency_alert = models.DateTimeField(null=True, blank=True)
    last_email_sent = models.DateTimeField(null=True, blank=True)

    ######Utility Methods

    def calculate_bmi(self):
        if self.height and self.weight:
            return self.weight / ((self.height / 100) ** 2)
        return None

    def calculate_severity(self):
        score = 0
        symptom_text = self.symptoms.lower()

        # Age factor
        if self.age >= 60:
            score += 2
        elif self.age >= 45:
            score += 1

        # BMI factor
        if self.bmi:
            if self.bmi >= 30:
                score += 2
            elif self.bmi >= 25:
                score += 1

        # Heart history
        if self.heart_history:
            score += 3

        #Symptom-based scoring 

        symptom_weights = {
            "chest pain": 3,
            "shortness of breath": 3,
            "fever": 2,
            "cough": 1,
            "cold": 1,
            "headache": 1,
            "nausea": 1,
            "dizziness": 2,
            "fatigue": 1,
            "vomiting": 2
        }

        for symptom, weight in symptom_weights.items():
            if symptom in symptom_text:
                score += weight

        #Final Severity Classification

        if score >= 8:
            return "High"
        elif score >= 4:
            return "Moderate"
        else:
            return "Mild"

    def save(self, *args, **kwargs):

        # Calculate BMI
        self.bmi = self.calculate_bmi()

        # Clean symptoms
        symptom_list = []
        if self.symptoms:
            symptom_list = [s.strip().lower() for s in self.symptoms.split(",") if s.strip()]

        try:
            # ML prediction
            self.severity = predict_severity(
                self.age,
                self.bmi,
                symptom_list,
                self.heart_history
            )

        except Exception:
            # Fallback to rule-based method
            self.severity = self.calculate_severity()

        super().save(*args, **kwargs)