from django.db import models

from common.models import TimeStampedModel
from accounts.models import ClientUser, GeneralPracticeUser, Patient
from .model_choices import *


class Instruction(TimeStampedModel, models.Model):
    client_user = models.ForeignKey(ClientUser, on_delete=models.CASCADE, verbose_name='Client')
    gp_user = models.ForeignKey(GeneralPracticeUser, on_delete=models.CASCADE, verbose_name='GP Allocated', null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name='Patient')
    completed_signed_off_timestamp = models.DateTimeField(null=True, blank=True)
    rejected_timestamp = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)
    type = models.CharField(max_length=4, choices=INSTRUCTION_TYPE_CHOICES)
    final_report_date = models.TextField(blank=True)
    initial_monetary_value = models.FloatField(null=True, blank=True, verbose_name='Value £')
    status = models.IntegerField(choices=INSTRUCTION_STATUS_CHOICES, default=INSTRUCTION_STATUS_NEW)
    consent_form = models.FileField(upload_to='consent_forms', null=True)

    class Meta:
        verbose_name = "Instruction"
        ordering = ('-created',)

    def __str__(self):
        return self.client_user.user.first_name + "::" + self.patient.user.first_name


class InstructionAdditionQuestion(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE)
    question = models.TextField(blank=True)
    response_mandatory = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Instruction Addition Question"

    def __str__(self):
        return self.question


class InstructionConditionsOfInterest(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE)
    readcode2_code = models.CharField(max_length=255, blank=True)
    SNOMEDCT_code = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Instruction Conditions Of Interest"

    def __str__(self):
        return self.readcode2_code + ': ' + self.SNOMEDCT_code