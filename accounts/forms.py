from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings

from common.functions import verify_password
from .models import Patient, GeneralPracticeUser, ClientUser, TITLE_CHOICE, GENERAL_PRACTICE_USER, User
from instructions.models import InstructionPatient
DATE_INPUT_FORMATS = settings.DATE_INPUT_FORMATS


class MyChoiceField(forms.ChoiceField):

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')


class InstructionPatientForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), required=False)
    patient_dob = forms.DateField(
        input_formats=DATE_INPUT_FORMATS, required=True,
        widget=forms.DateInput(attrs={'autocomplete': 'off', 'placeholder': ''})
    )
    patient_postcode = MyChoiceField(required=True, label='Address postcode')
    patient_address_number = MyChoiceField(required=False, label='Address name number')
    patient_address_line1 = forms.CharField(max_length=255, required=True)
    patient_address_line2 = forms.CharField(max_length=255, required=True)
    patient_address_line3 = forms.CharField(max_length=255, required=True)
    patient_city = forms.CharField(max_length=255, required=True)
    patient_country = forms.CharField(max_length=255, required=True)

    class Meta:
        model = InstructionPatient
        exclude = ('instruction', 'patient_user')
        widgets = {
            'patient_postcode': forms.TextInput(attrs={'placeholder': '', }),
            'patient_dob': forms.DateTimeInput(attrs={'placeholder': '', 'autocomplete': 'off'}),
            'patient_address_number': forms.TextInput(attrs={'placeholder': '', })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_data = kwargs.get('initial')
        if initial_data:
            edit_patient = initial_data.get('edit_patient')
            if not edit_patient:
                post_code = initial_data.get('patient_postcode')
                address_number = initial_data.get('patient_address_number')
                if post_code:
                    self.fields['patient_postcode'] = forms.CharField(max_length=255, label='Address postcode')

                if address_number:
                    self.fields['patient_address_number'] = forms.CharField(max_length=255, label='Address name number')

                self.fields['patient_title'] = forms.CharField(max_length=255, label='Title*')


class GPForm(forms.Form):
    gp_title = forms.ChoiceField(choices=TITLE_CHOICE, required=False)
    initial = forms.CharField(max_length=255, required=False, label='Initials', widget=forms.TextInput(attrs={'placeholder': ''}))
    gp_last_name = forms.CharField(max_length=255, required=False, label='Last Name', widget=forms.TextInput(attrs={'id': 'gp_last_name', 'name': 'gp_last_name', 'placeholder': '',}))

    class Meta:
        model = GeneralPracticeUser
        fields = ('gp_title', 'initial', 'gp_last_name')

        labels = {
            'gp_title': 'Title'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_data = kwargs.get('initial')
        if initial_data:
            self.fields['gp_title'] = forms.CharField(max_length=255, label='Title')


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

    def clean_email1(self):
        email = self.cleaned_data.get('email1')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This GP Surgery with this email already exists ')
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        first_name = self.cleaned_data.get('first_name')
        surname = self.cleaned_data.get('surname')
        email = self.cleaned_data.get('email1')
        password_auth = verify_password(password, first_name, surname, email)
        if not password_auth.get('verified'):
            raise forms.ValidationError(password_auth.get('warning'))
        return password

    def clean_email1(self):
        email = self.cleaned_data.get('email1')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address has already been used to register.')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if User.objects.filter(first_name=first_name).exists():
            raise forms.ValidationError('This GP Surgery with this name already exists ')
        return first_name

    def save__with_gp(self, gp_organisation=None):
        gp_manager_user = User.objects._create_user(
            email=self.cleaned_data.get('email1'),
            username=self.cleaned_data.get('first_name'),
            password=self.cleaned_data.get('password1'),
            first_name=self.cleaned_data.get('first_name'),
            type=GENERAL_PRACTICE_USER,
            is_staff=True,
        )
        gp_user_data = {'user': gp_manager_user, 'role': GeneralPracticeUser.PRACTICE_MANAGER}
        if gp_organisation:
            gp_user_data['organisation'] = gp_organisation
        general_practice_user = GeneralPracticeUser.objects.create(**gp_user_data)

        return {
            'general_pratice_user': general_practice_user,
            'password': gp_manager_user.password
        }


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
