from django import forms
from .models import Patient, GeneralPracticeUser


class PatientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255, required=True, label='First name*', widget=forms.TextInput(attrs={'placeholder': ''}))
    last_name = forms.CharField(max_length=255, required=True, label='Last name*', widget=forms.TextInput(attrs={'placeholder': ''}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': ''}), required=True)

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
    last_name = forms.CharField(max_length=255, required=True, label='Last Name*', widget=forms.TextInput(attrs={'placeholder': ''}))

    class Meta:
        model = GeneralPracticeUser
        fields = ('title', 'initial', 'last_name')

        labels = {
            'title': 'Title*'
        }