from django import forms
from django.forms.models import modelformset_factory

from .models import Library


class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = ('key', 'value')


LibraryFormset = modelformset_factory(
    Library,
    form=LibraryForm
)