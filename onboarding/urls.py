from django.urls import path
from . import views

app_name = 'onboarding'
urlpatterns = (
    path('emr_setup/', views.emr_setup, name='emr_setup'),
)
