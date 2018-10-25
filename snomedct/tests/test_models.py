from django.test import TestCase
from model_mommy import mommy

from snomedct.models import (
    SnomedConcept, ReadCode, SnomedDescendant, CommonSnomedConcepts
)


class SnomedConceptTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.snomedct = mommy.make(
            SnomedConcept, fsn_description='fsn_description',
            external_id=1234567890
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.snomedct),
            f'{self.snomedct.pk} - fsn_description'
        )


class ReadCodeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        snomedct = mommy.make(SnomedConcept, fsn_description='fsn_description')
        cls.readcode = mommy.make(
            ReadCode, ext_read_code='12345', concept_id=snomedct
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.readcode), f'{self.readcode.pk} - fsn_description - 12345'
        )


class SnomedDescendantTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.snomedct = mommy.make(SnomedConcept, fsn_description='fsn_description')
        cls.snomed_descendant = mommy.make(
            SnomedDescendant, descendant_external_id=cls.snomedct,
            external_id=cls.snomedct
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.snomed_descendant),
            f'{self.snomed_descendant.pk} - fsn_description - {self.snomedct.pk} - fsn_description'
        )


class CommonSnomedConceptsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.snomedct = mommy.make(
            SnomedConcept, fsn_description='fsn_description',
            external_id=1234567890
        )
        cls.common_snomed_concepts = mommy.make(
            CommonSnomedConcepts, common_name='Heart Disease', snomed_concept_code=[cls.snomedct]
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.common_snomed_concepts), 'Heart Disease'
        )
