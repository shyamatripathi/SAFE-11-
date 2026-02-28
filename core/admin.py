
# Register your models here.
from django.contrib import admin
from .models import HealthProfile

@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "bmi", "severity")