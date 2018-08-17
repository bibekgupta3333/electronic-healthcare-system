from django.urls import path

from . import views

app_name = 'services'
urlpatterns = [
    path('getpatientlist', views.getPatientList, name='getpatientlist'),
    path('getpatientrecord', views.getPatientRecord, name='getpatientrecord'),
    path('getpatientattachment', views.getPatientAttachment, name='getpatientattachment'),
]