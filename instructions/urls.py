from django.urls import path
from . import views

app_name = 'instructions'
urlpatterns = (
    path('view_data/', views.instruction, name='view_data'),
)