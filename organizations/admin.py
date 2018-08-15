from django.contrib import admin
from django import forms
from .models import *


class OrganizationClientForm(forms.ModelForm):
    class Meta:
        model = OrganizationClient
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
        model = OrganizationGeneralPractice
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


admin.site.register(OrganizationClient, OrganizationClientAdmin)
admin.site.register(OrganizationGeneralPractice, OrganizationGeneralPracticeAdmin)