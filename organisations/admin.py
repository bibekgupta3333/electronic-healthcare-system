from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django import forms
from .models import OrganisationMedidata, OrganisationGeneralPractice, OrganisationClient, NHSGeneralPractice


class NHSGeneralPracticeResource(resources.ModelResource):
    class Meta:
        model = NHSGeneralPractice
        import_id_fields = ('code', )

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        NHSGeneralPractice.objects.all().delete()


class NHSGeneralPracticeAdmin(ImportExportModelAdmin):
    skip_admin_log = True
    resource_class = NHSGeneralPracticeResource
    list_display = ('name', 'code')

    def get_queryset(self, request):
        qs = super(NHSGeneralPracticeAdmin, self).get_queryset(request)
        qs = qs.order_by('name')
        return qs


class OrganisationClientForm(forms.ModelForm):
    class Meta:
        model = OrganisationClient
        fields = '__all__'


class OrganisationClientAdmin(admin.ModelAdmin):
    form = OrganisationClientForm
    fieldsets = (
        ('Organisation Information', {'fields': ('trading_name', 'legal_name', 'address', 'type')}),
        ('Addition Information', {
            'classes': ('hidden', 'additionInfo'),
            'fields': ('contact_name', 'contact_telephone', 'contact_email', 'generic_telephone', 'generic_email',
                       'fax_number', 'companies_house_number', 'vat_number')}),
        ('Insurance: Addition Information', {
            'classes': ('hidden', 'Insurance'),
            'fields': ('division', 'fca_number')}),
        ('Consent Type', {'fields': ('can_create_amra', 'can_create_sars')}),
    )

    class Media:
        js = ('js/custom_admin/organisation_admin.js', )


class OrganisationGeneralPracticeForm(forms.ModelForm):
    class Meta:
        model = OrganisationGeneralPractice
        fields = '__all__'


class OrganisationGeneralPracticeAdmin(admin.ModelAdmin):
    form = OrganisationGeneralPracticeForm
    fieldsets = (
        ('Organisation Information', {'fields': ('trading_name', 'legal_name', 'address', 'companies_house_number', 'vat_number',
                                    'practice_code')}),
        ('Operating Information', {'fields': ('operating_system', 'operating_system_socket_endpoint', 'operating_system_auth_token')}),
        ('Contact Information', {'fields': ('contact_name', 'contact_telephone', 'contact_email',
                                'generic_telephone', 'generic_email', 'fax_number')}),
        ('Payment Information', {'fields': ('payment_timing', 'payment_bank_holder_name', 'payment_bank_sort_code',
                                            'payment_bank_account_number', 'payment_preference')})
    )


class OrganisationMedidataAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        query_set = super(OrganisationMedidataAdmin, self).get_queryset(request)
        client_organisation_query = OrganisationClient.objects.all()
        filtered_queryset = query_set.exclude(id__in=client_organisation_query)
        return filtered_queryset


admin.site.register(OrganisationClient, OrganisationClientAdmin)
admin.site.register(OrganisationGeneralPractice, OrganisationGeneralPracticeAdmin)
admin.site.register(OrganisationMedidata, OrganisationMedidataAdmin)
admin.site.register(NHSGeneralPractice, NHSGeneralPracticeAdmin)