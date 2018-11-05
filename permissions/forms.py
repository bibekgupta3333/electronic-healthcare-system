from django import forms
from permissions.models import InstructionPermission


class InstructionPermissionForm(forms.ModelForm):
    class Meta:
        model = InstructionPermission
        fields = ('__all__')
        widgets = {'organisation': forms.HiddenInput()}
