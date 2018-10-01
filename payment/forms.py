from django import forms
from .models import OrganisationFee


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

            return self.cleaned_data
        except KeyError:
            self._errors