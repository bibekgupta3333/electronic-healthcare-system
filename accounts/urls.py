from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = (
    path('view_account/', views.account_view, name='view_account'),
    path('view_users/', views.view_users, name='view_users'),
    path('create_user/', views.create_user, name='create_user'),
    path('manage_user/', views.manage_user, name='manage_user')
)