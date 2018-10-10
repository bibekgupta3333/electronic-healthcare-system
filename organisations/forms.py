from django import forms
from .models import NHSgpPractice, OrganisationGeneralPractice

# JT - what is going on here?
nhs_query = NHSgpPractice.objects.none()
gp_organisation = OrganisationGeneralPractice.objects.none()


class GeneralPracticeForm(forms.Form):
    gp_practice = forms.ModelChoiceField(queryset=nhs_query.union(gp_organisation))

    class Meta:
        model = NHSgpPractice
        fields = ('nhs')