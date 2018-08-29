from django.urls import path

from . import views

app_name = 'medicalreport'
urlpatterns = [
    path('edit', views.edit_report, name='edit'),
]
