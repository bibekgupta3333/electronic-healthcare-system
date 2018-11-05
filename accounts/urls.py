from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = (
    path('view-account/', views.account_view, name='view_account'),
    path('view-users/', views.view_users, name='view_users'),
    path('create-user/', views.create_user, name='create_user'),
    path('manage-user/', views.manage_user, name='manage_user'),
    path('check-email/', views.check_email, name='check_email')
)
