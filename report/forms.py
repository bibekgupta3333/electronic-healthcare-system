from django import forms

from .models import ThirdPartyAuthorisation

import datetime


class AccessCodeForm(forms.Form):
    access_code = forms.CharField(max_length=12, required=False)


class ThirdPartyAuthorisationForm(forms.ModelForm):
    error_messages = {
        'email_mismatch': "The two email fields didn't match.",
    }

    email_1 = forms.EmailField()
    email_2 = forms.EmailField()

    class Meta:
        model = ThirdPartyAuthorisation
        exclude = ('email', 'patient_report_auth', 'expired')

    def clean_email_2(self):
        email_1 = self.cleaned_data.get("email_1")
        email_2 = self.cleaned_data.get("email_2")
        if email_1 and email_2 and email_1 != email_2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch',
            )
        return email_2

    def save(self, report_auth, commit=True):
        third_party = super().save(commit=False)
        third_party.patient_report_auth = report_auth
        third_party.email = self.cleaned_data['email_2']
        third_party.expired = datetime.datetime.now().date() + datetime.timedelta(days=30)
        if third_party.modified:
            third_party.expired = third_party.modified + datetime.timedelta(days=30)

        if commit:
            third_party.save()

        return third_party
