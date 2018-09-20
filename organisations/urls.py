from django.urls import path
from . import views

app_name = 'organisations'
urlpatterns = (
    path('view_organisation/', views.create_organisation, name='create_organisation'),
    path('get_nhs_data/', views.get_nhs_data, name='get_nhs_data'),
    path('nhs_autocomplete/', views.get_nhs_autocomplete, name='nhs_autocomplete')
)