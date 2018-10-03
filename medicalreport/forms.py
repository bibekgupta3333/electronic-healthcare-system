from django import forms
from django.contrib import messages

from .models import AmendmentsForRecord


class MedicalReportFinaliseSubmitForm(forms.Form):
    prepared_and_signed = forms.ChoiceField(
        choices=AmendmentsForRecord.SUBMIT_OPTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'finaliseChoice'}),
        required=False,
    )
    prepared_by = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': '', 'placeholder': '', 'readonly': True}),
        required=False,
    )
    gp_practitioner = forms.ModelChoiceField(queryset=None, required=False)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['gp_practitioner'] = forms.ModelChoiceField(queryset=user.get_query_set_within_organisation(), required=False)

    def is_valid(self, post_data):
        super().is_valid()
        if post_data['event_flag'] == 'submit' and not post_data['gp_practitioner']:
            return False
        if post_data['prepared_and_signed'] == 'PREPARED_AND_SIGNED' and post_data['prepared_by']:
            return False

        return True

    def clean(self):
        super().clean()
        if self.cleaned_data['prepared_and_signed'] == 'PREPARED_AND_SIGNED':
            self.cleaned_data['prepared_by'] = ''

        return self.cleaned_data

