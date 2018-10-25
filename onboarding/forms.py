from django import forms
from onboarding.models import EMRSetup
from accounts import models as accounts_models


class EMRSetupForm(forms.ModelForm):
    class Meta:
        model = EMRSetup
        fields = ('__all__')


class SurgeryEmrSetUpStage2Form(forms.Form):
    surgery_name = forms.CharField(max_length=255, label='', disabled=True)
    surgery_code = forms.CharField(max_length=20, label='', disabled=True)
    address = forms.CharField(max_length=20, label='', disabled=True)
    postcode = forms.CharField(max_length=20, label='', disabled=True)
    surgery_tel_number = forms.CharField(max_length=20, label='', disabled=True)
    surgery_email = forms.CharField(max_length=255, label='', disabled=True)


class UserEmrSetUpStage2Form(forms.Form):
    title = forms.ChoiceField(choices=accounts_models.TITLE_CHOICE, label='')
    first_name = forms.CharField(max_length=255, label='')
    last_name = forms.CharField(max_length=255, label='')
    email = forms.EmailField(max_length=255, label='')
    role = forms.ChoiceField(choices=accounts_models.GeneralPracticeUser.ROLE_CHOICES, label='')
    gp_code = forms.CharField(max_length=255, required=False, label='')


class BankDetailsEmrSetUpStage2Form(forms.Form):
    min_fee_payments = 60.00
    level_1_payments = min_fee_payments*0.85
    level_2_payments = level_1_payments*0.90
    level_3_payments = level_2_payments*0.84

    bank_account_name = forms.CharField(max_length=255, label='')
    bank_account_number = forms.CharField(max_length=50, label='')
    bank_account_sort_code = forms.CharField(max_length=50, label='')
    received_within_3_days = forms.DecimalField(
        initial=60.00, max_value=80, min_value=60, max_digits=4, label='',
        widget=forms.NumberInput(attrs={'id': 'min_fee_payments'})
    )
    received_within_4_to_6_days = forms.DecimalField(
        initial=level_1_payments, max_digits=4, label='',
        widget=forms.NumberInput(attrs={'id': 'level_1_payments', 'readonly': True})
    )
    received_within_7_to_10_days = forms.DecimalField(
        initial=level_2_payments, max_digits=4, label='',
        widget=forms.NumberInput(attrs={'id': 'level_2_payments', 'readonly': True})
    )
    received_after_10_days = forms.DecimalField(
        initial=level_3_payments, max_digits=4, label='',
        widget=forms.NumberInput(attrs={'id': 'level_3_payments', 'readonly': True})
    )
    completed_by = forms.CharField(max_length=255, label='')
    job_title = forms.CharField(max_length=20, label='')

    def clean(self):
        super().clean()
        self.cleaned_data['received_within_3_days'] = round(self.cleaned_data['received_within_3_days'], 2)
        self.cleaned_data['received_within_4_to_6_days'] = round(self.cleaned_data['received_within_4_to_6_days'], 2)
        self.cleaned_data['received_within_7_to_10_days'] = round(self.cleaned_data['received_within_7_to_10_days'], 2)
        self.cleaned_data['received_after_10_days'] = round(self.cleaned_data['received_after_10_days'], 2)

        return self.cleaned_data
