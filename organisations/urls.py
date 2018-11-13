from django.urls import path
from . import views

app_name = 'organisations'
urlpatterns = (
    path('view-organisation/', views.create_organisation, name='create_organisation'),
    path('get-gporganisation-data/', views.get_gporganisation_data, name='get_gporganisation_data'),
    path('nhs-autocomplete/', views.get_nhs_autocomplete, name='nhs_autocomplete')
)