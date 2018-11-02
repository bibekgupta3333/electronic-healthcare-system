from django.urls import path
from . import views

app_name = 'organisations'
urlpatterns = (
    path('view-organisation/', views.create_organisation, name='create_organisation'),
    path('get-nhs-data/', views.get_nhs_data, name='get_nhs_data'),
    path('nhs-autocomplete/', views.get_nhs_autocomplete, name='nhs_autocomplete')
)