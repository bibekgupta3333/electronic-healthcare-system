from django.contrib import admin
from . import models
from django.shortcuts import get_object_or_404
from instructions.model_choices import INSTRUCTION_STATUS_REJECT


class InstructionConditionsInline(admin.TabularInline):
    model = models.InstructionConditionsOfInterest
    raw_id_fields = ('snomedct',)
    fields = ['snomedct',]

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.instructionconditionsofinterest_set.count():
            return 0
        else:
            return 1


class InstructionAdditionQuestionInline(admin.TabularInline):
    model = models.InstructionAdditionQuestion
    fields = ['question']

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.instructionconditionsofinterest_set.count():
            return 0
        else:
            return 1


class InstructionAdmin(admin.ModelAdmin):
    change_status = False
    list_display = ('client_user', 'gp_user', 'gp_practice', 'status', 'created')
    inlines = [
        InstructionConditionsInline,
        InstructionAdditionQuestionInline
    ]

    def save_model(self, request, obj, form, change):
        change_status = False
        if 'status' in form.changed_data:
            self.change_status = True
        super(InstructionAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super(InstructionAdmin, self).save_related(request, form, formsets, change)
        if self.change_status:
            pk = form.instance.id
            instruction = get_object_or_404(models.Instruction, pk=pk)
            if instruction.status == INSTRUCTION_STATUS_REJECT:
                if instruction.client_user:
                    instruction.send_reject_email([instruction.client_user.user.email, instruction.gp_user.user.email])
                else:
                    instruction.send_reject_email([instruction.gp_user.user.email])


admin.site.register(models.Instruction, InstructionAdmin)
admin.site.register(models.InstructionAdditionQuestion)
admin.site.register(models.Setting)
admin.site.register(models.InstructionPatient)
