from django import forms
from .models import OrganisationGeneralPractice

# JT - what is going on here?
gp_organisation = OrganisationGeneralPractice.objects.none()


class GeneralPracticeForm(forms.Form):
    gp_practice = forms.ModelChoiceField(queryset=gp_organisation)

    class Meta:
        model = OrganisationGeneralPractice
        fields = ('nhs')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_data = kwargs.get('initial')
        if initial_data:
            gp_practice = initial_data.get('gp_practice')
            if gp_practice:
                self.fields['gp_practice'] = forms.CharField(max_length=255)