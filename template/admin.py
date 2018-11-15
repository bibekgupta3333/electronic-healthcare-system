from django.contrib import admin

from .models import (
    TemplateInstruction, TemplateConditionsOfInterest, TemplateInstructionAdditionalQuestion
)


class TemplateConditionsInline(admin.TabularInline):
    model = TemplateConditionsOfInterest
    raw_id_fields = ('snomedct',)
    fields = ['snomedct']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.instructionconditionsofinterest_set.count():
            return 0
        else:
            return 1


class TemplateQuestionsInline(admin.TabularInline):
    model = TemplateInstructionAdditionalQuestion
    fields = ['question']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.instructionconditionsofinterest_set.count():
            return 0
        else:
            return 1


class TemplateInstructionAdmin(admin.ModelAdmin):
    search_fields = ['template_title', 'description', 'client_organisation']
    list_display = ('template_title', 'description', 'client_organisation')
    fields = ['template_title', 'description', 'client_organisation']
    inlines = [
        TemplateConditionsInline,
        TemplateQuestionsInline
    ]


admin.site.register(TemplateInstruction, TemplateInstructionAdmin)
