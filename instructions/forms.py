from django import forms
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError
from django.conf import settings

from instructions.model_choices import AMRA_TYPE, SARS_TYPE
from .models import InstructionAdditionQuestion, Instruction
from template.models import TemplateInstruction
from common.functions import multi_getattr
from snomedct.models import CommonSnomedConcepts
from accounts.models import User, GeneralPracticeUser


DATE_INPUT_FORMATS = settings.DATE_INPUT_FORMATS


class MyMultipleChoiceField(forms.MultipleChoiceField):

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')


class ScopeInstructionForm(forms.Form):
    type = forms.ChoiceField(choices=[], widget=forms.RadioSelect(attrs={'class': 'd-inline instructionType'}))
    template = forms.ModelChoiceField(queryset=TemplateInstruction.objects.none(), required=False)
    common_condition = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple(), required=False)
    addition_condition = MyMultipleChoiceField(required=False)
    addition_condition_title = forms.CharField(required=False, widget=forms.HiddenInput())
    consent_form = forms.FileField(required=False)
    send_to_patient = forms.BooleanField(widget=forms.CheckboxInput(), label='Send copy of medical report to patient?', required=False)

    def __init__(self, user=None, patient_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.type == 'CLT':
            self.fields['date_range_from'] = forms.DateField(input_formats=DATE_INPUT_FORMATS, required=False,
                                                             widget=forms.DateInput(attrs={'autocomplete': 'off', 'placeholder': 'From'}))
            self.fields['date_range_to'] = forms.DateField(input_formats=DATE_INPUT_FORMATS, required=False,
                                                           widget=forms.DateInput(attrs={'autocomplete': 'off', 'placeholder': 'To'}))
        initial_data = kwargs.get('initial')
        if initial_data:
            self.fields['type'] = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'w-25'}))
        else:
            self.patient_email = patient_email
            FORM_INSTRUCTION_TYPE_CHOICES = [
                (AMRA_TYPE, 'Underwriting(AMRA)'),
                (AMRA_TYPE, 'Claim(AMRA)'),
                (SARS_TYPE, 'SAR')
            ]

            SCOPE_COMMON_CONDITION_CHOICES = [
                [[snomed.external_id for snomed in common_snomed.snomed_concept_code.all()], common_snomed.common_name] for common_snomed in CommonSnomedConcepts.objects.all()
            ]

            self.fields['common_condition'] = forms.MultipleChoiceField(choices=SCOPE_COMMON_CONDITION_CHOICES, widget=forms.CheckboxSelectMultiple(), required=False)

            client_organisation = multi_getattr(user, 'userprofilebase.clientuser.organisation', default=None)
            if client_organisation:
                if not client_organisation.can_create_amra and not client_organisation.can_create_sars:
                    FORM_INSTRUCTION_TYPE_CHOICES = ()
                elif not client_organisation.can_create_amra:
                    del FORM_INSTRUCTION_TYPE_CHOICES[0]
                    del FORM_INSTRUCTION_TYPE_CHOICES[0]
                elif not client_organisation.can_create_sars:
                    del FORM_INSTRUCTION_TYPE_CHOICES[2]

            gp_organisation = multi_getattr(user, 'userprofilebase.generalpracticeuser.organisation', default=None)
            if gp_organisation:
                del FORM_INSTRUCTION_TYPE_CHOICES[0]
                del FORM_INSTRUCTION_TYPE_CHOICES[0]

            self.fields['type'] = forms.ChoiceField(
                choices=FORM_INSTRUCTION_TYPE_CHOICES,
                widget=forms.RadioSelect(
                    attrs={'class': 'd-inline instructionType'}
                )
            )

    def clean(self):
        super().clean()
        if self.cleaned_data.get('type') == "AMRA" and not self.patient_email and not self.cleaned_data['consent_form']:
            raise ValidationError(
                "You must supply a valid consent form, or the patient's e-mail address when creating an AMRA instruction!")
        return self.cleaned_data


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
        'question': forms.TextInput(attrs={'class': 'form-control questions_inputs'}, ),
    },
)


class SarsConsentForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = ('sars_consent', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MdxConsentForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = ('mdx_consent', )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)