from django.db import models


# Create your models here.
class SnomedConcept(models.Model):
    external_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    fsn_description = models.CharField(max_length=255)
    external_fsn_description_id = models.BigIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['fsn_description']),
            models.Index(fields=['external_id']),
        ]

    def snomed_descendants(self):
        result = SnomedConcept.objects.filter(snomeddescendant__external_id=self.external_id)
        print(result)
        return result


class ReadCode(models.Model):
    ext_read_code = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    concept_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE, db_column="concept_id")

    class Meta:
        indexes = [
            models.Index(fields=['concept_id']),
        ]


class SnomedDescendant(models.Model):
    descendant_external_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE, db_column="descendant_external_id")
    external_id = models.BigIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['external_id']),
        ]
