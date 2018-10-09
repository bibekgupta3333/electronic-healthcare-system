from django.urls import path
from . import views

app_name = 'template'
urlpatterns = (
    path('create/', views.TemplateCreate.as_view(), name='create'),
    path('list/', views.TemplateList.as_view(), name='list'),
    path('details/<int:pk>/', views.TemplateDetails.as_view(), name='details'),
    path('search/', views.TemplateSearch.as_view(), name='search'),
    path('edit/<int:pk>/', views.TemplateEdit.as_view(), name='edit'),
)
