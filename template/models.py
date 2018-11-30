from django.db import models

from organisations.models import OrganisationClient
from instructions.model_choices import INSTRUCTION_TYPE_CHOICES
from snomedct.models import SnomedConcept
from accounts.models import User
from common.models import TimeStampedModel


class TemplateInstruction(TimeStampedModel, models.Model):
    client_organisation = models.ForeignKey(OrganisationClient, null=True, on_delete=models.CASCADE, blank=True)
    template_title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    type = models.CharField(max_length=4, choices=INSTRUCTION_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Template of Instruction'

    def __str__(self):
        return self.template_title


class TemplateInstructionAdditionalQuestion(models.Model):
    FORMAT_NUMBER = 'NUM'
    FORMAT_TEXT = 'TXT'

    TEMPLATE_FORMAT_ANSWER = (
        (FORMAT_NUMBER, 'Number'),
        (FORMAT_TEXT, 'Text')
    )

    template_instruction = models.ForeignKey(TemplateInstruction, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    response_mandatory = models.BooleanField(default=False)
    answer_format = models.CharField(max_length=3, choices=TEMPLATE_FORMAT_ANSWER)

    class Meta:
        verbose_name = 'Template Instruction Additional Question'

    def __str__(self):
        return self.question


class TemplateConditionsOfInterest(models.Model):
    template_instruction = models.ForeignKey(TemplateInstruction, on_delete=models.CASCADE)
    snomedct = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Template Conditions Of Interest"

    def __str__(self) -> str:
        return "{} ({})".format(self.snomedct.fsn_description, self.snomedct.external_id)
