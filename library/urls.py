from django.urls import path
from . import views

app_name = 'library'
urlpatterns = (
    path('', views.edit_library, name='edit_library'),
)