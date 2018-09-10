from django import forms
from .models import NHSgpPractice


class NHSgpPracticeForm(forms.Form):
    nhs = forms.ModelChoiceField(queryset=NHSgpPractice.objects.all())

    class Meta:
        model = NHSgpPractice
        fields = ('nhs')