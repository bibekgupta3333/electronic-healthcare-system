from django.contrib import admin
from . import models
from django.shortcuts import get_object_or_404
from common.import_export import CustomExport
from instructions.model_choices import INSTRUCTION_STATUS_REJECT
from django.utils import timezone
from datetime import timedelta


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


class DaysSinceFilter(admin.SimpleListFilter):
    title = 'Days since created'
    parameter_name = 'created_date'

    MORE_THAN_0 = 5
    MORE_THAN_5 = 10
    MORE_THAN_10 = 15
    MORE_THAN_15 = 0

    def lookups(self, request, model_admin):
        return [
            (self.MORE_THAN_0, '0 to 5 days'),
            (self.MORE_THAN_5, '6 to 10 days'),
            (self.MORE_THAN_10, '11 to 15 days'),
            (self.MORE_THAN_15, 'More than 15 days')
        ]

    def queryset(self, request, queryset):
        days = None
        if self.value():
            days = int(self.value())
        if days == self.MORE_THAN_0:
            date = timezone.now() - timedelta(days=self.MORE_THAN_0)
            return queryset.filter(created__gt=date)
        elif days == self.MORE_THAN_5:
            date_from = timezone.now() - timedelta(days=self.MORE_THAN_5)
            date_to = timezone.now() - timedelta(days=self.MORE_THAN_0)
            return queryset.filter(created__gt=date_from, created__lte=date_to)
        elif days == self.MORE_THAN_10:
            date_from = timezone.now() - timedelta(days=self.MORE_THAN_10)
            date_to = timezone.now() - timedelta(days=self.MORE_THAN_5)
            return queryset.filter(created__gt=date_from, created__lte=date_to)
        elif days == self.MORE_THAN_15:
            date = timezone.now() - timedelta(days=self.MORE_THAN_10)
            return queryset.filter(created__lt=date)
        else:
            return queryset


class InstructionAdmin(CustomExport, admin.ModelAdmin):
    change_status = False
    list_display = ('client_user', 'gp_practice', 'status', 'created', 'type', 'days_since_created')
    list_filter = ('type', DaysSinceFilter, 'gp_user', 'client_user')
    search_fields = [
        'gp_user__userprofilebase_ptr__user__first_name',
        'client_user__userprofilebase_ptr__user__first_name',
        'gp_user__userprofilebase_ptr__user__last_name',
        'client_user__userprofilebase_ptr__user__last_name',
        'type'
    ]
    inlines = [
        InstructionConditionsInline,
        InstructionAdditionQuestionInline
    ]

    def days_since_created(self, instance):
        return (timezone.now().date() - instance.created.date()).days

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
