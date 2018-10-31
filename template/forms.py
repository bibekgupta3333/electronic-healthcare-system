from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import (
    TemplateInstruction, TemplateInstructionAdditionalQuestion, TemplateConditionsOfInterest
)


class TemplateInstructionForm(forms.ModelForm):
    class Meta:
        model = TemplateInstruction
        fields = ('template_title', 'description', 'client_organisation', 'created_by')
        widgets = {
            'template_title': forms.TextInput(attrs={'id': 'template_title'}, ),
            'description': forms.Textarea(attrs={'id': 'template_description'}, ),
        }


class TemplateInstructionAdditionalQuestionForm(forms.ModelForm):
    class Meta:
        model = TemplateInstructionAdditionalQuestion
        fields = ('question', 'template_instruction')


class TemplateConditionsOfInterestForm(forms.ModelForm):
    class Meta:
        model = TemplateConditionsOfInterest
        fields = '__all__'


TemplateInstructionAdditionalQuestionFormset = inlineformset_factory(
    TemplateInstruction, TemplateInstructionAdditionalQuestion,
    form=TemplateInstructionAdditionalQuestionForm, extra=1,
    can_delete=False, fields=('question', 'template_instruction'))

TemplateConditionsOfInterestFormset = inlineformset_factory(
    TemplateInstruction, TemplateConditionsOfInterest,
    form=TemplateConditionsOfInterestForm, extra=1,
    can_delete=False, fields=('snomedct', ))

