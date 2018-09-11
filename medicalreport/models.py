from django.db import models
from django.contrib.postgres.fields import JSONField
from instructions.models import Instruction
from snomedct.models import SnomedConcept


# Create your models here.
class Redaction (models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE)
    consultation_notes = models.TextField()
    acute_prescription_notes = models.TextField()
    repeat_prescription_notes = models.TextField()
    referral_notes = models.TextField()
    significant_problem_notes = models.TextField()
    attachment_notes = models.TextField()
    bloods_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    redacted_xpaths = JSONField()


class AdditionalMedicationRecords(models.Model):
    drug = models.CharField(max_length=255)
    dose = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    snomed_concept = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE)
    redaction = models.ForeignKey(Redaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prescribed_from = models.DateField()
    prescribed_to = models.DateField()
    notes = models.TextField()
    repeat = models.BooleanField()


class AdditionalAllergies(models.Model):
    allergen = models.CharField(max_length=255)
    reaction = models.CharField(max_length=255)
    date_discovered = models.DateField()
    redaction = models.ForeignKey(Redaction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
