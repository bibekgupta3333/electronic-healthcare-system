from django import forms
from .models import Patient, GeneralPracticeUser
from medi.settings.common import DATE_INPUT_FORMATS


class PatientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255, required=True, label='First name*', widget=forms.TextInput(attrs={'placeholder': ''}))
    last_name = forms.CharField(max_length=255, required=True, label='Last name*', widget=forms.TextInput(attrs={'placeholder': ''}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), required=True)
    date_of_birth = forms.DateField(input_formats=DATE_INPUT_FORMATS, widget=forms.DateInput(attrs={'palceholder': ''}))

    class Meta:
        model = Patient
        fields = ('title', 'first_name', 'last_name', 'date_of_birth', 'address_postcode', 'address_name_number',
                  'nhs_number', 'email')
        widgets = {
            'address_postcode': forms.TextInput(attrs={'placeholder': '', }, ),
            'date_of_birth': forms.DateTimeInput(attrs={'placeholder': '', 'autocomplete': 'off'}, ),
            'address_name_number': forms.TextInput(attrs={'placeholder': '', },)
        }

        labels = {
            'title': 'Title*',
            'address_postcode': 'Postcode*',
            'address_name_number': 'Select address*',
        }


class GPForm(forms.ModelForm):
    initial = forms.CharField(max_length=255, required=True, label='Initials*', widget=forms.TextInput(attrs={'placeholder': ''}))
    last_name = forms.CharField(max_length=255, required=True, label='Last Name*', widget=forms.TextInput(attrs={'id': 'gp_last_name', 'placeholder': '',}))

    class Meta:
        model = GeneralPracticeUser
        fields = ('title', 'initial', 'last_name')

        labels = {
            'title': 'Title*'
        }


class NewUserForm(forms.ModelForm):
    
    first_name = forms.CharField(max_length=255, required=True, label='', widget=forms.TextInput())
    last_name = forms.CharField(max_length=255, required=True, label='', widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), label='', required=True)
    username = forms.CharField(max_length=255, required=True, label='', widget=forms.TextInput())
    password = forms.CharField(required=True, widget=forms.HiddenInput())
    send_email = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = GeneralPracticeUser
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'send_email', 'role', 'payment_bank_holder_name',
                    'payment_bank_account_number', 'payment_bank_sort_code')
        widgets = {
            'payment_bank_sort_code': forms.HiddenInput(attrs={'placeholder': '', })
        }
        labels = {
            'payment_bank_holder_name': '',
            'payment_bank_account_number': '',
            'payment_bank_sort_code': ''
        }