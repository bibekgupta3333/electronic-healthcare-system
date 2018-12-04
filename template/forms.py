from django import forms
from django.forms.models import modelformset_factory
from .models import TemplateInstruction, TemplateAdditionalQuestion


class TemplateAdditionalQuestionForm(forms.ModelForm):
    class Meta:
        model = TemplateAdditionalQuestion
        fields = ('question',)


TemplateAdditionalQuestionFormset = modelformset_factory(
    TemplateAdditionalQuestion,
    form=TemplateAdditionalQuestionForm,
    fields = ('question',),
    extra=1,
    widgets={
        'question': forms.TextInput(attrs={'class': 'form-control questions_inputs'}, ),
    }
)
