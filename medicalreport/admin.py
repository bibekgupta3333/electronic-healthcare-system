from django.contrib import admin
from medicalreport.models import ReferencePhrases, AmendmentsForRecord


class ReferencePhrasesAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


admin.site.register(ReferencePhrases, ReferencePhrasesAdmin)