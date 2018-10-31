from django import forms
from django.core.exceptions import ValidationError
from .models import Patient, GeneralPracticeUser, ClientUser, TITLE_CHOICE

from django.conf import settings
DATE_INPUT_FORMATS = settings.DATE_INPUT_FORMATS


class MyChoiceField(forms.ChoiceField):

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')


class PatientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255, required=True, label='First name*', widget=forms.TextInput(attrs={'placeholder': ''}))
    last_name = forms.CharField(max_length=255, required=True, label='Last name*', widget=forms.TextInput(attrs={'placeholder': ''}))
    date_of_birth = forms.DateField(input_formats=DATE_INPUT_FORMATS, required=True, widget=forms.DateInput(attrs={'autocomplete': 'off', 'placeholder': ''}))
    address_postcode = MyChoiceField(required=True, )
    address_name_number = MyChoiceField(required=False)

    class Meta:
        model = Patient
        fields = ('title', 'first_name', 'last_name', 'date_of_birth', 'address_postcode', 'address_name_number',
                  'nhs_number', 'patient_input_email')
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_data = kwargs.get('initial')
        if initial_data:
            post_code = initial_data.get('address_postcode')
            if post_code:
                self.fields['address_postcode'] = forms.CharField(max_length=255)
            self.fields['title'] = forms.CharField(max_length=255)


class GPForm(forms.Form):
    gp_title = forms.ChoiceField(choices=TITLE_CHOICE, required=False)
    initial = forms.CharField(max_length=255, required=False, label='Initials', widget=forms.TextInput(attrs={'placeholder': ''}))
    last_name = forms.CharField(max_length=255, required=False, label='Last Name', widget=forms.TextInput(attrs={'id': 'gp_last_name', 'name': 'gp_last_name', 'placeholder': '',}))

    class Meta:
        model = GeneralPracticeUser
        fields = ('title', 'initial', 'last_name')

        labels = {
            'gp_title': 'Title'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_data = kwargs.get('initial')
        if initial_data:
            self.fields['title'] = forms.CharField(max_length=255)


class PMForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255, required=True, label='')
    surname = forms.CharField(max_length=255, required=True, label='')
    email1 = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), label='', required=True)
    email2 = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), label='', required=True)
    password1 = forms.CharField(required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(required=True, widget=forms.PasswordInput())

    class Meta:
        model = GeneralPracticeUser
        fields = ('first_name', 'surname', 'email1', 'email2', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initial_data = kwargs.get('initial')

class NewGPForm(forms.ModelForm):
    
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

class NewClientForm(forms.ModelForm):
    
    first_name = forms.CharField(max_length=255, required=True, label='', widget=forms.TextInput())
    last_name = forms.CharField(max_length=255, required=True, label='', widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), label='', required=True)
    username = forms.CharField(max_length=255, required=True, label='', widget=forms.TextInput())
    password = forms.CharField(required=True, widget=forms.HiddenInput())
    send_email = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = ClientUser
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'send_email')
