from django.urls import path

from . import views

app_name = 'report'
urlpatterns = [
    path('<int:report_auth_id>/third-party-authorisation', views.add_third_party_authorisation, name='add-third-party'),
    path('<int:instruction_id>/<str:url>', views.sar_request_code, name='request-code'),
    path('access-code/<str:url>', views.sar_access_code, name='access-code'),
    path('select-report', views.get_report, name='select-report'),
    path('session-expired', views.session_expired, name='session-expired'),
]
