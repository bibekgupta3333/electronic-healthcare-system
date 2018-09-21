from django.urls import path

from . import views

app_name = 'snomedct'
urlpatterns = [
    path('query', views.query_snomed, name='query_snomed'),
    path('readcodes', views.get_readcords, name='get_readcords'),
    path('snomed-descendants', views.get_descendants, name='get_descendants'),
    path('descendant-readcodes', views.get_descendant_readcords, name='get_descendant_readcords'),
]
