from django.urls import path
from . import views

app_name = 'instructions'
urlpatterns = (
    path('view_pipeline/', views.instruction_pipeline_view, name='view_pipeline'),
    path('new_instruction/', views.new_instruction, name='new_instruction'),
    path('allocate_instruction/<int:instruction_id>', views.allocate_instruction, name='allocate_instruction')
)