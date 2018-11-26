from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = (
    path('view-account/', views.account_view, name='view_account'),
    path('view-users/', views.view_users, name='view_users'),
    path('create-user/', views.create_user, name='create_user'),
    path('medi-create-user/', views.medi_create_user, name='medi_create_user'),
    path('medi-change-user/<str:email>', views.medi_change_user, name='medi_change_user'),
    path('manage-user/', views.manage_user, name='manage_user'),
    path('verify-password/', views.verify_password, name='verify_password'),
    path('update-permission/', views.update_permission, name='update_permission'),
    path('check-email/', views.check_email, name='check_email')
)
