from django.db import models


# Create your models here.
class SnomedConcept(models.Model):
    # snomed_descendants = models.ForeignKey(SnomedDescendant, on_delete=models.CASCADE, null=True)
    # read_code = models.ForeignKey(ReadCode, on_delete=models.CASCADE, null=True)

    external_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    fsn_description = models.CharField(max_length=255)
    external_fsn_description_id = models.BigIntegerField()

    def snomed_descendants(self):
        result = SnomedDescendant.objects.filter(external_id=self.external_id)
        print(result)
        return result


class ReadCode(models.Model):
    ext_read_code = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    concept_id = models.BigIntegerField()
    # concept_id = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, to_field='external_id')


class SnomedDescendant(models.Model):
    external_id = models.BigIntegerField()
    # external_id = models.ForeignKey(SnomedConcept, on_delete=models.CASCADE, null=True)
    descendant_external_id = models.BigIntegerField()

    # snomed_concepts = models.ForeignKey('SnomedConcept', on_delete=models.CASCADE)
