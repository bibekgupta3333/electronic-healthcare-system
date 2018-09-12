from django import forms
from django.forms.models import modelformset_factory

from instructions.model_choices import INSTRUCTION_TYPE_CHOICES, AMRA_TYPE, SARS_TYPE
from .models import InstructionAdditionQuestion
from template.models import TemplateInstruction

CONDITION_HEART_DISEASE         = 0
CONDITION_LIVER_DISEASE         = 1
CONDITION_KIDNEY_DISEASE        = 2
CONDITION_MUSCULOSKELETAL       = 3
CONDITION_MOOD_DISORDERS        = 4
CONDITION_LUNG_DISEASE          = 5
CONDITION_DIABETES              = 6
CONDITION_INFLAMMATORY_BOWEL    = 7
CONDITION_CANCERS               = 8
CONDITION_NEURODEGENERATIVE     = 9


SCOPE_COMMON_CONDITION_CHOICES = (
    (CONDITION_HEART_DISEASE, 'Heart disease'),
    (CONDITION_LIVER_DISEASE, 'Liver disease'),
    (CONDITION_KIDNEY_DISEASE, 'Kidney disease'),
    (CONDITION_MUSCULOSKELETAL, 'Musculoskeletal'),
    (CONDITION_MOOD_DISORDERS, 'Mood disorders'),
    (CONDITION_LUNG_DISEASE, 'Lung disease'),
    (CONDITION_DIABETES, 'Diabetes'),
    (CONDITION_INFLAMMATORY_BOWEL, 'Inflammatory bowel'),
    (CONDITION_CANCERS, 'Cancers'),
    (CONDITION_NEURODEGENERATIVE, 'Neurodegenerative'),
)

FORM_INSTRUCTION_TYPE_CHOICES = (
    (AMRA_TYPE, 'Underwriting(AMRA)'),
    (AMRA_TYPE, 'Claim(AMRA)'),
    (SARS_TYPE, 'SAR')
)


class ScopeInstructionForm(forms.Form):
    type = forms.ChoiceField(choices=FORM_INSTRUCTION_TYPE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'd-inline'}))
    template = forms.CharField(max_length=255, required=False)
    # template = forms.ModelChoiceField(queryset=TemplateInstruction.objects.all(), required=False)
    common_condition = forms.MultipleChoiceField(choices=SCOPE_COMMON_CONDITION_CHOICES, widget=forms.CheckboxSelectMultiple(), required=False)
    addition_condition = forms.CharField(max_length=255, required=False)
    consent_form = forms.FileField(widget=forms.FileInput(attrs={'class': 'position-absolute'}), required=False)
    send_to_patient = forms.BooleanField(widget=forms.CheckboxInput(), label='Send copy of medical report to patient?', required=False)


class AdditionQuestionForm(forms.ModelForm):
    class Meta:
        model = InstructionAdditionQuestion
        fields = ('question',)


AdditionQuestionFormset = modelformset_factory(
        InstructionAdditionQuestion,
        form=AdditionQuestionForm,
        fields=('question', ),
        extra=1,
        widgets={
            'question': forms.TextInput(attrs={'class': 'form-control'}, ),
        },
    )

