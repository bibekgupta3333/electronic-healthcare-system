"""medi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.site.site_header = 'MediData administration'
admin.site.site_title = 'MediData administration'


urlpatterns = [
    path('testservices/', include('services.urls')),
    path('medicalreport/', include('medicalreport.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('instruction/', include('instructions.urls', namespace='instructions')),
    path('organisation/', include('organisations.urls', namespace='organisations')),
    path('select2/', include('django_select2.urls')),
]

urlpatterns += staticfiles_urlpatterns()
