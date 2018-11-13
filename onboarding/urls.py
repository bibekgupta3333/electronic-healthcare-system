from django.urls import path
from . import views

app_name = 'onboarding'
urlpatterns = (
    path('emr-setup/', views.emr_setup, name='emr_setup'),
    path('emr-setup-stage-2/<int:emrsetup_id>', views.emr_setup_stage_2, name='emr_setup_stage_2'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('code-autocomplete/', views.get_code_autocomplete, name='code_autocomplete'),
    path('name-autocomplete/', views.get_name_autocomplete, name='name_autocomplete'),
)
