from django.urls import path
from . import views

app_name = 'instructions'
urlpatterns = (
    path('view_pipeline/', views.instruction_pipeline_view, name='view_pipeline'),
    path('new_instruction/', views.new_instruction, name='new_instruction'),
    path('view_reject/<int:instruction_id>/', views.view_reject, name='view_reject'),
    path('upload_consent/<int:instruction_id>/', views.upload_consent, name='upload_consent'),
    path('review_instruction/<int:instruction_id>', views.review_instruction, name='review_instruction')
)
