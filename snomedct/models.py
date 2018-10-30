from django.db import models
from postgres_copy import CopyManager

from typing import Set


class SnomedConcept(models.Model):
    external_id = models.BigIntegerField(unique=True, primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    fsn_description = models.CharField(max_length=255)
    children = models.ManyToManyField(
        'self', through='SnomedDescendant', symmetrical=False,
        through_fields=('external_id', 'descendant_external_id')
    )
    external_fsn_description_id = models.BigIntegerField()
    objects = CopyManager()

    def __str__(self):
        return "{} - {}".format(self.external_id, self.fsn_description)

    class Meta:
        indexes = [
            models.Index(fields=['fsn_description']),
            models.Index(fields=['external_id']),
        ]

    def descendants(self, include_self=True) -> Set['SnomedConcept']:
        descendants = set()
        if include_self:
            descendants.add(self)
        for child in self.children.all():
            descendants.update(child.descendants(include_self=True))
        return descendants

    def descendant_readcodes(self):
        """
        Return readcodes of this snomed concept and its descendants.
        """
        return ReadCode.objects.filter(concept_id__in=self.descendants())

    def readcodes(self):
        return ReadCode.objects.filter(concept_id=self.external_id)

    def is_descendant_of(self, snomed_concept: 'SnomedConcept') -> bool:
        return self in snomed_concept.descendants()


class ReadCode(models.Model):
    ext_read_code = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    file_path = models.CharField(max_length=255)
    concept_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE, db_column="concept_id", null=True)
    objects = CopyManager()

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.concept_id.fsn_description, self.ext_read_code)

    class Meta:
        indexes = [
            models.Index(fields=['concept_id']),
        ]

    def is_descendant_of_snomed_concept(self, snomed_concept: SnomedConcept) -> bool:
        return self in snomed_concept.descendant_readcodes()


class SnomedDescendant(models.Model):
    descendant_external_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE,
                                               db_column="descendant_external_id", null=True, related_name='descendant_external_id')
    external_id = models.ForeignKey(SnomedConcept, to_field='external_id', on_delete=models.CASCADE,
                                    db_column="external_id", null=True, related_name='external_ids')
    objects = CopyManager()

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.descendant_external_id.fsn_description, self.external_id)

    class Meta:
        indexes = [
            models.Index(fields=['external_id']),
        ]


class CommonSnomedConcepts(models.Model):
    common_name = models.CharField(max_length=255)
    snomed_concept_code = models.ManyToManyField(SnomedConcept)

    def __str__(self):
        return self.common_name