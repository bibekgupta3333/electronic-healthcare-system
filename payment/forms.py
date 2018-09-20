from django import forms
from .models import OrganisationFee


class OrganisationFeeForm(forms.ModelForm):

    class Meta:
        model = OrganisationFee
        fields = '__all__'

    def clean(self):
        try:
            max_day_lvl_1 = self.cleaned_data['max_day_lvl_1']
            max_day_lvl_2 = self.cleaned_data['max_day_lvl_2']
            max_day_lvl_3 = self.cleaned_data['max_day_lvl_3']
            if max_day_lvl_1 >= max_day_lvl_3:
                raise forms.ValidationError("Day are incorrect: Max day lvl 3 must more than Max day lvl 1")

            if max_day_lvl_1 >= max_day_lvl_2:
                raise forms.ValidationError("Day are incorrect: Max day lvl 2 must more than Max day lvl 1")

            if max_day_lvl_2 >= max_day_lvl_3:
                raise forms.ValidationError("Day are incorrect: Max day lvl 3 must more than Max day lvl 2")

            return self.cleaned_data
        except KeyError:
            self._errors