from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = (
    path('view_account/', views.account_view, name='view_account'),
)