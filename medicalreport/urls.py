from django.urls import path

from . import views

app_name = 'medicalreport'
urlpatterns = [
    path('<int:instruction_id>/edit/', views.edit_report, name='edit_report'),
    path('<int:instruction_id>/update/', views.update_report, name='update_report'),
]
