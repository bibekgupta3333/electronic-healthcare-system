from django.urls import path
from . import views

app_name = 'onboarding'
urlpatterns = (
    path('emr_setup/', views.emr_setup, name='emr_setup'),
    path('emr_setup_stage_2/<int:emrsetup_id>', views.emr_setup_stage_2, name='emr_setup_stage_2'),
    path('sign_up/', views.sign_up, name='sign_up')
)
