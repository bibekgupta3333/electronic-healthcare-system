from django.test import TestCase
from django.test import tag
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

    @tag('notimplemented')
    def test_snomed_descendants(self):
        self.fail('Not implemented')

    @tag('notimplemented')
    def test_snomed_descendant_readcodes(self):
        self.fail('Not implemented')

    @tag('notimplemented')
    def test_readcodes(self):
        self.fail('Not implemented')


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
        snomedct = mommy.make(SnomedConcept, fsn_description='fsn_description')
        cls.snomed_descendant = mommy.make(
            SnomedDescendant, descendant_external_id=snomedct,
            external_id='12345'
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.snomed_descendant),
            f'{self.snomed_descendant.pk} - fsn_description - 12345'
        )


class CommonSnomedConceptsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.common_snomed_concepts = mommy.make(
            CommonSnomedConcepts, common_name='Heart Disease', snomed_concept_code=[1234567890,]
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.common_snomed_concepts), 'Heart Disease'
        )
