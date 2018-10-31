from django.contrib import admin

from .models import (
    TemplateInstruction, TemplateConditionsOfInterest, TemplateInstructionAdditionalQuestion
)


class TemplateConditionsInline(admin.TabularInline):
    model = TemplateConditionsOfInterest
    fields = ['snomedct']


class TemplateQuestionsInline(admin.TabularInline):
    model = TemplateInstructionAdditionalQuestion
    fields = ['question']


class TemplateInstructionAdmin(admin.ModelAdmin):
    search_fields = ['template_title', 'description', 'client_organisation']
    list_display = ('template_title', 'description', 'client_organisation')
    fields = ['template_title', 'description', 'client_organisation']
    inlines = [
        TemplateConditionsInline,
        TemplateQuestionsInline
    ]


admin.site.register(TemplateInstruction, TemplateInstructionAdmin)
