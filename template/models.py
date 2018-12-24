from django.db import models

from organisations.models import OrganisationClient
from instructions.model_choices import INSTRUCTION_TYPE_CHOICES
from snomedct.models import SnomedConcept, CommonSnomedConcepts
from accounts.models import ClientUser
from organisations.models import OrganisationClient
from common.models import TimeStampedModel

COMMON = 'common'
ADDITION = 'addition'

CONDITION_TYPE = (
    (COMMON, 'Common'),
    (ADDITION, 'Addition')
)


class TemplateInstruction(TimeStampedModel, models.Model):
    template_title = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=4, choices=INSTRUCTION_TYPE_CHOICES)
    organisation = models.ForeignKey(OrganisationClient, null=True, on_delete=models.CASCADE, blank=True)
    created_by = models.ForeignKey(ClientUser, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Template of Instruction'

    def __str__(self):
        return self.template_title


class TemplateAdditionalQuestion(models.Model):
    template_instruction = models.ForeignKey(TemplateInstruction, on_delete=models.CASCADE)
    question = models.CharField(max_length=255, blank=True)
    response_mandatory = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Template Instruction Additional Question'

    def __str__(self):
        return self.question


class TemplateConditionsOfInterest(models.Model):

    template_instruction = models.ForeignKey(TemplateInstruction, on_delete=models.CASCADE)
    snomedct = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Template Conditions Of Interest"

    def __str__(self) -> str:
        return "{} ({})".format(self.snomedct.fsn_description, self.snomedct.external_id)


class TemplateCommonCondition(models.Model):

    template_instruction = models.ForeignKey(TemplateInstruction, on_delete=models.CASCADE)
    common_condition = models.ForeignKey(CommonSnomedConcepts, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Template Common Conditions"

    def __str__(self) -> str:
        return "{}".format(self.common_condition.common_name)


class TemplateAdditionCondition(models.Model):
    template_instruction = models.ForeignKey(TemplateInstruction, on_delete=models.CASCADE)
    snomedct = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Template Additional Conditions"

    def __str__(self) -> str:
        return "{} ({})".format(self.snomedct.fsn_description, self.snomedct.external_id)