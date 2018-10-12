from django import forms
from django.utils.html import format_html

from .models import OrganisationFee
from django.conf import settings
SITE_NAME = settings.SITE_NAME


class OrganisationFeeForm(forms.ModelForm):
    max_day_lvl_3 = forms.IntegerField(required=False,label='Min day lvl 3', widget=forms.NumberInput(attrs={'class': 'vIntegerField'}))

    class Meta:
        model = OrganisationFee
        fields = '__all__'

    def clean(self):
        try:
            self.cleaned_data['max_day_lvl_3'] = self.cleaned_data['max_day_lvl_2'] + 1
            if self.cleaned_data['max_day_lvl_1'] >= self.cleaned_data['max_day_lvl_3']:
                raise forms.ValidationError("Day are incorrect: Max day lvl 3 must more than Max day lvl 1")

            if self.cleaned_data['max_day_lvl_1'] >= self.cleaned_data['max_day_lvl_2']:
                raise forms.ValidationError("Day are incorrect: Max day lvl 2 must more than Max day lvl 1")

            if self.cleaned_data['max_day_lvl_2'] >= self.cleaned_data['max_day_lvl_3']:
                raise forms.ValidationError("Day are incorrect: Max day lvl 3 must more than Max day lvl 2")

            organisation_gp = self.cleaned_data['gp_practice']
            organisation_fee = OrganisationFee.objects.filter(gp_practice=organisation_gp).first()
            owning_gp = ''
            if self.initial:
                owning_gp = self.initial['gp_practice']

            if owning_gp:
                if organisation_fee and organisation_gp.pk != owning_gp:
                    raise forms.ValidationError(
                        format_html(
                            '<strong>Organisation Had selected:</strong> <a href="{site_name}admin/payment/organisationfee/{id}/change/">Here</a>'.format(
                                id=organisation_fee.pk,
                                site_name=SITE_NAME
                            )
                        )
                    )
            else:
                if organisation_fee:
                    raise forms.ValidationError(
                        format_html(
                            '<strong>Organisation Had selected:</strong> <a href="{site_name}admin/payment/organisationfee/{id}/change/">Here</a>'.format(
                                id=organisation_fee.pk,
                                site_name=SITE_NAME
                            )
                        )
                    )

            return self.cleaned_data
        except KeyError:
            self._errors