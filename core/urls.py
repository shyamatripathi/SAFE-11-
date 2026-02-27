from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path("", lambda request: redirect("register")),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
]