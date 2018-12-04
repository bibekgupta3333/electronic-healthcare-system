from django import forms
from permissions.models import InstructionPermission
from instructions.models import Instruction
from accounts.models import GeneralPracticeUser
from django.contrib.auth.models import Permission, Group


exclude_permission = (
    'add_instruction',
    'change_instruction',
    'delete_instruction',
    'view_instruction'
)


class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name


class InstructionPermissionForm(forms.ModelForm):
    permissions = MyModelMultipleChoiceField(
        Permission.objects.filter(content_type__model=Instruction._meta.model_name).exclude(codename__in=exclude_permission),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-permissions'}),
        required=False
    )

    class Meta:
        model = InstructionPermission
        fields = ('__all__')
        widgets = {
            'organisation': forms.HiddenInput(),
            'role': forms.Select(attrs={'disabled': 'true', 'class': 'permission-role'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance') and kwargs['instance'].group:
            self.initial['permissions'] = kwargs['instance'].group.permissions.all()


class GroupPermissionForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('__all__')
