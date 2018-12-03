from django.contrib import admin

from .models import (
    TemplateInstruction, TemplateConditionsOfInterest, TemplateAdditionalQuestion
)


class TemplateConditionsInline(admin.TabularInline):
    model = TemplateConditionsOfInterest
    raw_id_fields = ('snomedct',)
    fields = ['snomedct']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.templateconditionsofinterest_set.count():
            return 0
        else:
            return 1


class TemplateQuestionsInline(admin.TabularInline):
    model = TemplateAdditionalQuestion
    fields = ['question']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.templateadditionalquestion_set.count():
            return 0
        else:
            return 1


class TemplateInstructionAdmin(admin.ModelAdmin):
    search_fields = ['template_title', 'description', 'organisation', 'created_by']
    list_display = ('template_title', 'description', 'organisation', 'created_by')
    fields = ['template_title', 'description', 'organisation', 'created_by']
    inlines = [
        TemplateConditionsInline,
        TemplateQuestionsInline
    ]


admin.site.register(TemplateInstruction, TemplateInstructionAdmin)
