from django import forms


class AccessCodeForm(forms.Form):
    access_code = forms.CharField(max_length=12, required=False)
