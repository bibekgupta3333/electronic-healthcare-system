from django.contrib import admin
from . import models
from django.shortcuts import get_object_or_404
from common.import_export import CustomImportExport
from instructions.model_choices import INSTRUCTION_STATUS_REJECT
from django.utils import timezone
from datetime import timedelta
from instructions.models import Instruction
from django.db.models import Q
from organisations.models import OrganisationGeneralPractice
from instructions.forms import ClientNoteForm


class InstructionReminder(admin.TabularInline):
    model = models.InstructionReminder
    readonly_fields = ('note', 'created_date', 'reminder_day')
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class InstructionClientNote(admin.TabularInline):
    model = models.InstructionClientNote
    readonly_fields = ('created_date', 'created_by')
    form = ClientNoteForm
    extra = 0


class InstructionInternalNote(admin.TabularInline):
    model = models.InstructionInternalNote
    readonly_fields = ('created_date', 'created_by')
    fields = ['note', 'created_date', 'created_by']
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


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


class ClientOrgFilter(admin.SimpleListFilter):
    title = 'Client'
    parameter_name = 'organisation'

    def lookups(self, request, model_admin):
        organisations = set()
        for data in Instruction.objects.filter(client_user__isnull=False, client_user__organisation__isnull=False):
            organisation = data.client_user.organisation
            organisations.add((organisation.pk, organisation.trading_name))
        return organisations

    def queryset(self, request, queryset):
        organisation_id = self.value()
        if organisation_id:
            organisation_id = int(organisation_id)
            return queryset.filter(client_user__isnull=False, client_user__organisation_id=organisation_id)
        return queryset


class GPOrgFilter(admin.SimpleListFilter):
    title = 'GP Practice'
    parameter_name = 'gp_pratice'

    def lookups(self, request, model_admin):
        organisations = set()
        for data in Instruction.objects.filter(gp_practice_id__isnull=False, gp_practice_type__isnull=False):
            organisation = data.gp_practice
            if organisation:
                organisations.add((organisation.pk, organisation.name))
        return organisations

    def queryset(self, request, queryset):
        organisation_pk = self.value()
        if organisation_pk:
            return queryset.filter(gp_practice_id__isnull=False, gp_practice_id=organisation_pk)
        return queryset


class InstructionAdmin(CustomImportExport, admin.ModelAdmin):
    change_status = False
    list_display = ('gp_practice', 'client', 'status', 'created', 'type', 'days_since_created')
    list_filter = ('type', DaysSinceFilter, ClientOrgFilter, GPOrgFilter)
    readonly_fields = ('medi_ref',)
    actions = ['export_status_report_as_csv', 'export_payment_as_csv']
    search_fields = [
        'type'
    ]
    inlines = [
        InstructionReminder,
        InstructionClientNote,
        InstructionInternalNote,
        InstructionConditionsInline,
        InstructionAdditionQuestionInline
    ]

    def get_search_results(self, request, queryset, search_term):
        gp_organisations = [gp_org.pk for gp_org in OrganisationGeneralPractice.objects.filter(name__icontains=search_term)]
        queryset = queryset.filter(
            Q(type__icontains=search_term) |
            Q(gp_practice_id__in=gp_organisations) |
            Q(client_user__organisation__trading_name__icontains=search_term)
        )
        return queryset, False

    def client(self, instance):
        client_organisation = ''
        if instance.client_user:
            client_organisation = instance.client_user.organisation.__str__()
        return client_organisation

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

    def save_formset(self, request, form, formset, change):
        if formset.model == models.InstructionInternalNote or formset.model == models.InstructionClientNote:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.created_by = request.user
                instance.save()
            formset.save_m2m()
        super(InstructionAdmin, self).save_formset(request, form, formset, change)


admin.site.register(models.Instruction, InstructionAdmin)
admin.site.register(models.InstructionAdditionQuestion)
admin.site.register(models.Setting)
admin.site.register(models.ClientNote)
admin.site.register(models.InstructionPatient)
