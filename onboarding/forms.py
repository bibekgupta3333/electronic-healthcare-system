from django import forms

from accounts import models as accounts_models
from accounts.models import GpPractices

q = GpPractices.objects.none()
from organisations.models import OrganisationGeneralPractice
from .models import EMRSetup


class EMRSetupForm(forms.ModelForm):
    surgery_code = forms.CharField()
    surgery_name = forms.CharField()

    class Meta:
        model = EMRSetup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['surgery_code'] = forms.CharField(widget=forms.Select(choices=GpPractices.objects.all().values_list('id', 'sitenumber_c')))
        self.fields['surgery_name'] = forms.CharField(widget=forms.Select(choices=GpPractices.objects.all().values_list('id', 'name')))

        initial_data = kwargs.get('initial')
        if initial_data:
            surgery_code = initial_data.get('surgery_code')
            surgery_name = initial_data.get('surgery_name')
            if surgery_name:
                self.fields['surgery_name'] = forms.CharField(max_length=255)
            if surgery_code:
                self.fields['surgery_code'] = forms.ChoiceField(mmax_length=255)

    def clean(self):
        cleaned_data = super().clean()
        surgery_code = cleaned_data.get('surgery_code')
        surgery_name = cleaned_data.get('surgery_name')

        if EMRSetup.objects.filter(surgery_code=surgery_code, surgery_name=surgery_name).exists():
            raise forms.ValidationError('This GP Surgery has already been created.'
                                        ' Please contact MediData for more information')
        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        surgery_code = cleaned_data.get('surgery_code')
        surgery_name = cleaned_data.get('surgery_name')

        if EMRSetup.objects.filter(surgery_code=surgery_code, surgery_name=surgery_name).exists():
            raise forms.ValidationError('This GP Surgery has already been created.'
                                        ' Please contact MediData for more information')
        return cleaned_data


class SurgeryForm(forms.Form):
    surgery_name = forms.ChoiceField(choices=[])
    practice_code = forms.ChoiceField(choices=[])
    postcode = forms.ChoiceField(choices=[])
    address = forms.ChoiceField(choices=[])
    address_line1 = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    address_line2 = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    address_line3 = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    city = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    country = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    contact_num = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    emis_org_code = forms.CharField(max_length=20, label='', widget=forms.TextInput())
    operating_system = forms.ChoiceField(choices=OrganisationGeneralPractice.GP_OP_SYS_CHOICES, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['operating_system'] = 'EW'
        # initial_data = kwargs.get('initial')

    def clean_practice_code(self):
        practice_code = self.cleaned_data.get('practice_code')

        if OrganisationGeneralPractice.objects.filter(practice_code=practice_code).exists():
            raise forms.ValidationError('This GP Surgery with this practice code already exists ')
        return practice_code

    def clean_surgery_name(self):
        surgery_name = self.cleaned_data.get('surgery_name')
        if OrganisationGeneralPractice.objects.filter(trading_name=surgery_name).exists():
            raise forms.ValidationError('This GP Surgery with this name already exists ')
        return surgery_name

    def clean_address_line1(self):
        address_line1 = self.cleaned_data.get('address_line1')
        if OrganisationGeneralPractice.objects.filter(billing_address_street__startswith=address_line1).exists():
            raise forms.ValidationError('This GP Surgery with this address already exists ')
        return address_line1

    def validate_operating_system(self):
        operating_system = self.cleaned_data.get('operating_system')
        if not operating_system == 'EW':
            self.cleaned_data['accept_policy'] = False
        return operating_system

    def save(self, commit=True):
        gp_address = ' '.join([
            self.cleaned_data.get('address_line1'),
            self.cleaned_data.get('address_line2') if self.cleaned_data.get('address_line2') else '',
            self.cleaned_data.get('city'),
            self.cleaned_data.get('postcode')
        ])
        accept_policy = True if self.data.get('accept_policy') == 'on' else False
        gp_organisation = OrganisationGeneralPractice.objects.create(
            trading_name=self.cleaned_data.get('surgery_name'),
            accept_policy=accept_policy,
            legal_name=self.cleaned_data.get('surgery_name'),
            address=gp_address,
            contact_telephone=self.cleaned_data.get('contact_num'),
            practice_code=self.cleaned_data.get('practice_code'),
        )
        return gp_organisation


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
