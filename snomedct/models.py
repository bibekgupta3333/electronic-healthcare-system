from django.db import models
from postgres_copy import CopyManager


# Create your models here.
class SnomedConcept(models.Model):
    external_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    fsn_description = models.CharField(max_length=255)
    external_fsn_description_id = models.BigIntegerField()
    objects = CopyManager()

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.fsn_description, self.external_id)

    class Meta:
        indexes = [
            models.Index(fields=['fsn_description']),
            models.Index(fields=['external_id']),
        ]

    def snomed_descendants(self):
        return SnomedConcept.objects.filter(snomeddescendant__external_id=self.external_id)

    def snomed_descendant_readcodes(self):
        return ReadCode.objects.filter(concept_id__snomeddescendant__external_id=self.external_id)

    def readcodes(self):
        return ReadCode.objects.filter(concept_id=self.external_id)


class ReadCode(models.Model):
    ext_read_code = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    concept_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE, db_column="concept_id")
    objects = CopyManager()

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.concept_id.fsn_description, self.ext_read_code)

    class Meta:
        indexes = [
            models.Index(fields=['concept_id']),
        ]


class SnomedDescendant(models.Model):
    descendant_external_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE, db_column="descendant_external_id")
    external_id = models.BigIntegerField()
    objects = CopyManager()

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.descendant_external_id.fsn_description, self.external_id)

    class Meta:
        indexes = [
            models.Index(fields=['external_id']),
        ]


class CommonSnomedConcepts(models.Model):
    snomed_concept = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.snomed_concept.fsn_description, self.snomed_concept.external_id)
