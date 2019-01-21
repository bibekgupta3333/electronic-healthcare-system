from django.db import models
from django.contrib.postgres.fields import JSONField
from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_COMPLETE
from snomedct.models import SnomedConcept
from accounts.models import User, GeneralPracticeUser
from django.utils.html import format_html


class AmendmentsForRecord(models.Model):
    REDACTION_STATUS_NEW = 'NEW'
    REDACTION_STATUS_DRAFT = 'DRAFT'
    REDACTION_STATUS_SUBMIT = 'SUBMIT'

    REDACTION_STATUS_CHOICES = (
        (REDACTION_STATUS_NEW, 'New'),
        (REDACTION_STATUS_DRAFT, 'Draft'),
        (REDACTION_STATUS_SUBMIT, 'Submit')
    )

    PREPARED_AND_SIGNED = 'PREPARED_AND_SIGNED'
    PREPARED_AND_REVIEWED = 'PREPARED_AND_REVIEWED'

    SUBMIT_OPTION_CHOICES = (
        (PREPARED_AND_SIGNED, 'Prepared and signed directly by {}'),
        (PREPARED_AND_REVIEWED, format_html('Signed off by <span id="preparer"></span>')),
    )

    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE)
    consultation_notes = models.TextField(blank=True)
    acute_prescription_notes = models.TextField(blank=True)
    repeat_prescription_notes = models.TextField(blank=True)
    referral_notes = models.TextField(blank=True)
    significant_problem_notes = models.TextField(blank=True)
    attachment_notes = models.TextField(blank=True)
    bloods_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    redacted_xpaths = JSONField(null=True)
    re_redacted_codes = JSONField(null=True)
    submit_choice = models.CharField(max_length=255, choices=SUBMIT_OPTION_CHOICES, blank=True)
    review_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    prepared_by = models.ForeignKey(GeneralPracticeUser, on_delete=models.CASCADE, null=True)
    status = models.CharField(choices=REDACTION_STATUS_CHOICES, max_length=6, default=REDACTION_STATUS_NEW)
    comment_notes = models.TextField(blank=True)
    instruction_checked = models.BooleanField(default=False, blank=True, null=True)

    @property
    def patient_emis_number(self) -> str:
        return self.instruction.patient.emis_number

    def get_gp_name(self) -> str:
        gp_name = ''
        if self.instruction.status == INSTRUCTION_STATUS_COMPLETE:
            if self.prepared_by:
                gp_name = self.prepared_by
        return gp_name

    def additional_acute_medications(self):
        return AdditionalMedicationRecords.objects.filter(amendments_for_record=self.id, repeat=False)

    def additional_repeat_medications(self):
        return AdditionalMedicationRecords.objects.filter(amendments_for_record=self.id, repeat=True)

    def additional_allergies(self):
        return AdditionalAllergies.objects.filter(amendments_for_record=self.id)

    def redacted(self, xpaths) -> bool:
        if self.redacted_xpaths is not None:
            return all(xpath in self.redacted_xpaths for xpath in xpaths)
        else:
            return False


class AdditionalMedicationRecords(models.Model):
    drug = models.CharField(max_length=255)
    dose = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    snomed_concept = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, null=True)
    amendments_for_record = models.ForeignKey(AmendmentsForRecord, on_delete=models.CASCADE)
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
    amendments_for_record = models.ForeignKey(AmendmentsForRecord, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NhsSensitiveConditions(models.Model):
    group = models.CharField(max_length=128)
    snome_code = models.CharField(max_length=128)


class ReferencePhrases(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
