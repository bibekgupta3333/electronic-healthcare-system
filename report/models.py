from django.db import models

from common.models import TimeStampedModel
from accounts.models import Patient


class PatientReportAuth(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    instruction = models.ForeignKey('instructions.Instruction', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    token = models.CharField(max_length=6, null=True)
    url = models.CharField(max_length=256)
