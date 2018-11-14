from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django import forms
from .models import OrganisationMedidata, OrganisationGeneralPractice, OrganisationClient


class OrganisationGeneralPracticeResource(resources.ModelResource):
    class Meta:
        model = OrganisationGeneralPractice
        import_id_fields = ('practcode',)
        skip_unchanged = True

    def skip_row(self, instance, original):
        if OrganisationGeneralPractice.objects.filter(practcode=instance.practcode).exists():
            print("duplicate: {code}".format(code=instance.practcode))
            return True
        return super().skip_row(instance, original)


class OrganisationGeneralPracticeForm(forms.ModelForm):
    class Meta:
        model = OrganisationGeneralPractice
        fields = '__all__'


class OrganisationGeneralPracticeAdmin(ImportExportModelAdmin):
    skip_admin_log = True
    resource_class = OrganisationGeneralPracticeResource
    form = OrganisationGeneralPracticeForm
    list_display = ('name', 'practcode')

    def get_queryset(self, request):
        qs = super(OrganisationGeneralPracticeAdmin, self).get_queryset(request)
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


class OrganisationMedidataAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        query_set = super(OrganisationMedidataAdmin, self).get_queryset(request)
        client_organisation_query = OrganisationClient.objects.all()
        filtered_queryset = query_set.exclude(id__in=client_organisation_query)
        return filtered_queryset


admin.site.register(OrganisationClient, OrganisationClientAdmin)
admin.site.register(OrganisationGeneralPractice, OrganisationGeneralPracticeAdmin)
admin.site.register(OrganisationMedidata, OrganisationMedidataAdmin)