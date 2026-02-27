from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class HealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    age = models.IntegerField()
    height = models.FloatField()  # in cm
    weight = models.FloatField()  # in kg
    bmi = models.FloatField(blank=True, null=True)

    symptoms = models.TextField()
    heart_history = models.BooleanField(default=False)

    severity = models.CharField(max_length=20, blank=True)

    def calculate_bmi(self):
        return self.weight / ((self.height / 100) ** 2)

    def calculate_severity(self):
        score = 0

        if self.age > 60:
            score += 2

        if self.bmi and self.bmi > 30:
            score += 2

        if "chest pain" in self.symptoms.lower():
            score += 3

        if self.heart_history:
            score += 3

        if score >= 6:
            return "High"
        elif score >= 3:
            return "Moderate"
        else:
            return "Mild"

    def save(self, *args, **kwargs):
        self.bmi = self.calculate_bmi()
        self.severity = self.calculate_severity()
        super().save(*args, **kwargs)