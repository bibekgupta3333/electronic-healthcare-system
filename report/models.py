from django.db import models
from common.models import TimeStampedModel
from accounts.models import Patient
from django.contrib.auth.forms import UserCreationForm


class PatientReportAuth(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    instruction = models.ForeignKey('instructions.Instruction', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    mobi_request_id = models.CharField(max_length=255, blank=True)
    verify_pin = models.CharField(max_length=6, blank=True)
    url = models.CharField(max_length=256)
    locked_report = models.BooleanField(default=False)

    def __str__(self):
        return '%s : %s'%(self.instruction.__str__(), self.patient.__str__())


class ThirdPartyAuthorisation(TimeStampedModel):
    patient_report_auth = models.ForeignKey(PatientReportAuth, on_delete=models.CASCADE, related_name='third_parties', null=True)
    company = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    case_reference = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    family_phone_number = models.CharField(max_length=20)
    office_phone_number = models.CharField(max_length=20)
    expired = models.DateField(null=True)

    def __str__(self):
        return self.company


