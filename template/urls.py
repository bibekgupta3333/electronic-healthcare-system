from django.urls import path
from . import views

app_name = 'template'
urlpatterns = (
    path('create/', views.template_create_or_update, name='create_template'),
    path('view-templates/', views.template_views, name='view_templates'),
    path('template-autocomplete/', views.template_autocomplete, name='template_autocomplete'),
    path('get-template-data/', views.get_template_data, name='template_data'),
    path('new-template/', views.template_new, name='new_template'),
    path('edit-template/<int:template_id>/', views.template_edit, name='edit_template'),
    path('remove-template/', views.template_remove, name='remove_template')
)
