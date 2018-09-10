from django.urls import path
from . import views

app_name = 'instructions'
urlpatterns = (
    path('view_data/', views.instruction_pipeline_view, name='view_data'),
    path('new_instruction/', views.new_instruction, name='new_instruction'),
)