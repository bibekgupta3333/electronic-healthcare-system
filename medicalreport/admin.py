from django.contrib import admin
from medicalreport.models import ReferencePhrases, AmendmentsForRecord


admin.site.register(ReferencePhrases)
admin.site.register(AmendmentsForRecord)
