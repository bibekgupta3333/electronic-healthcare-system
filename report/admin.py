from django.contrib import admin
from .models import PatientReportAuth, ThirdPartyAuthorisation

# Register your models here.
admin.site.register(PatientReportAuth)
admin.site.register(ThirdPartyAuthorisation)