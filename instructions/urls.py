from django.urls import path
from . import views

app_name = 'instructions'
urlpatterns = (
    path('view-pipeline/', views.instruction_pipeline_view, name='view_pipeline'),
    path('new-instruction/', views.new_instruction, name='new_instruction'),
    path('view-reject/<int:instruction_id>/', views.view_reject, name='view_reject'),
    path('upload-consent/<int:instruction_id>/', views.upload_consent, name='upload_consent'),
    path('review-instruction/<int:instruction_id>', views.review_instruction, name='review_instruction'),
    path('api-get-address/<str:address>', views.api_get_address, name='api_get_address'),
    path('consent-contact/<int:instruction_id>/select-patient/<int:patient_emis_number>', views.consent_contact, name='consent_contact'),
    path('print-mdx-consent/<int:instruction_id>/patient/<int:patient_emis_number>', views.print_mdx_consent, name='print_mdx_consent'),
    path('view-fail/<int:instruction_id>/', views.view_fail, name='view_fail')
)
