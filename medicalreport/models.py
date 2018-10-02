from django.db import models
from django.contrib.postgres.fields import JSONField
from instructions.models import Instruction
from snomedct.models import SnomedConcept
from accounts.models import User


# Create your models here.
class Redaction (models.Model):
    REDACTION_STATUS_NEW = 'NEW'
    REDACTION_STATUS_DRAFT = 'DRAFT'
    REDACTION_STATUS_SUBMIT = 'SUBMIT'

    REDACTION_STATUS_CHOICES = (
        (REDACTION_STATUS_NEW, 'New'),
        (REDACTION_STATUS_DRAFT, 'Draft'),
        (REDACTION_STATUS_SUBMIT, 'Submit')
    )

    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE)
    consultation_notes = models.TextField(null=True)
    acute_prescription_notes = models.TextField(null=True)
    repeat_prescription_notes = models.TextField(null=True)
    referral_notes = models.TextField(null=True)
    significant_problem_notes = models.TextField(null=True)
    attachment_notes = models.TextField(null=True)
    bloods_notes = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    patient_emis_number = models.CharField(max_length=255, null=True, default=None)
    redacted_xpaths = JSONField(null=True)
    review_by = models.ForeignKey(User, on_delete=models.CASCADE)
    prepared_by = models.CharField(max_length=255, blank=True)
    status = models.CharField(choices=REDACTION_STATUS_CHOICES, max_length=6, default=REDACTION_STATUS_NEW)

    def additional_acute_medications(self):
        return AdditionalMedicationRecords.objects.filter(redaction=self.id, repeat=False)

    def additional_repeat_medications(self):
        return AdditionalMedicationRecords.objects.filter(redaction=self.id, repeat=True)

    def additional_allergies(self):
        return AdditionalAllergies.objects.filter(redaction=self.id)

    def redacted(self, xpaths):
        if self.redacted_xpaths is not None:
            return all(xpath in self.redacted_xpaths for xpath in xpaths)
        else:
            return False


class AdditionalMedicationRecords(models.Model):
    drug = models.CharField(max_length=255)
    dose = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    snomed_concept = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, null=True)
    redaction = models.ForeignKey(Redaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prescribed_from = models.DateField(null=True)
    prescribed_to = models.DateField(null=True)
    notes = models.TextField()
    repeat = models.BooleanField()


class AdditionalAllergies(models.Model):
    allergen = models.CharField(max_length=255)
    reaction = models.CharField(max_length=255)
    date_discovered = models.DateField(null=True)
    redaction = models.ForeignKey(Redaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
