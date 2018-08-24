from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django import forms
from .models import OrganisationMedidata, OrganisationGeneralPractice, OrganisationClient, NHSgpPractice


class NHSgpPracticeResource(resources.ModelResource):
    class Meta:
        model = NHSgpPractice
        import_id_fields = ('code', )

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        NHSgpPractice.objects.all().delete()


class NHSgpPracticeAdmin(ImportExportModelAdmin):
    resource_class = NHSgpPracticeResource


class OrganizationClientForm(forms.ModelForm):
    class Meta:
        model = OrganisationClient
        fields = '__all__'


class OrganizationClientAdmin(admin.ModelAdmin):
    form = OrganizationClientForm
    fieldsets = (
        ('Organisation Information', {'fields': ('trading_name', 'legal_name', 'address', 'type')}),
        ('Addition Information', {
            'classes': ('hidden', 'additionInfo'),
            'fields': ('contact_name', 'contact_telephone', 'contact_email', 'generic_telephone', 'generic_email',
                       'fax_number', 'companies_house_number', 'vat_number')}),
        ('Insurance: Addition Information', {
            'classes': ('hidden', 'Insurance'),
            'fields': ('division', 'fca_number')}),
    )

    class Media:
        js = ('js/custom_admin/organisation_admin.js', )


class OrganizationGeneralPracticeForm(forms.ModelForm):
    class Meta:
        model = OrganisationGeneralPractice
        fields = '__all__'


class OrganizationGeneralPracticeAdmin(admin.ModelAdmin):
    form = OrganizationGeneralPracticeForm
    fieldsets = (
        ('Organisation Information', {'fields': ('trading_name', 'legal_name', 'address', 'companies_house_number', 'vat_number',
                                    'practice_code')}),
        ('Operating Information', {'fields': ('operating_system', 'operating_system_socket_endpoint', 'operating_system_auth_token')}),
        ('Contact Information', {'fields': ('contact_name', 'contact_telephone', 'contact_email',
                                'generic_telephone', 'generic_email', 'fax_number')}),
        ('Payment Information', {'fields': ('payment_timing', 'payment_bank_holder_name', 'payment_bank_sort_code',
                                            'payment_bank_account_number')})
    )


class OrganizationMedidataAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        query_set = super(OrganizationMedidataAdmin, self).get_queryset(request)
        client_organisation_query = OrganisationClient.objects.all()
        filtered_queryset = query_set.exclude(id__in=client_organisation_query)
        return filtered_queryset


admin.site.register(OrganisationClient, OrganizationClientAdmin)
admin.site.register(OrganisationGeneralPractice, OrganizationGeneralPracticeAdmin)
admin.site.register(OrganisationMedidata, OrganizationMedidataAdmin)
admin.site.register(NHSgpPractice, NHSgpPracticeAdmin)