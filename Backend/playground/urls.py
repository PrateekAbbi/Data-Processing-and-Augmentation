from django.urls import path
from . import views

urlpatterns = [
    path("fetchIncidents/", views.fetch_incidents)
]