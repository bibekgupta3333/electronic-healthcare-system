from django import forms
from accounts.models import GeneralPracticeUser
from django.utils.html import format_html


class MedicalReportFinaliseSubmitForm(forms.Form):
    SUBMIT_OPTION_CHOICES = (
        ('PREPARED_AND_SIGNED', 'Prepared and signed directly by'),
        ('PREPARED_AND_REVIEWED', format_html('Prepared by <span id="preparer"></span>  and reviewed by')),
    )
    prepared_and_signed = forms.ChoiceField(
        choices=SUBMIT_OPTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'finaliseChoice'}),
        required=False,
    )
    prepared_by = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': '', 'placeholder': '',}),
        required=False,
    )
    gp_practitioner = forms.ModelChoiceField(queryset=None)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['gp_practitioner'] = forms.ModelChoiceField(queryset=user.get_query_set_within_organisation())
