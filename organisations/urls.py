from django.urls import path
from . import views

app_name = 'organisations'
urlpatterns = (
    path('view_data/', views.create_organisation, name='create_organisation'),
)