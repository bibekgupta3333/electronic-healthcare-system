from django import forms
from onboarding.models import EMRSetup


class EMRSetupForm(forms.ModelForm):
    class Meta:
        model = EMRSetup
        fields = ('__all__')
