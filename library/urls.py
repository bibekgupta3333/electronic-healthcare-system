from django.urls import path
from . import views

app_name = 'library'
urlpatterns = (
    path('<str:event>/', views.edit_library, name='edit_library'),
    path('delete/<int:library_id>/', views.delete_library, name='delete_library'),
    path('edit/<int:library_id>/', views.edit_word_library, name='edit_word_library'),
)