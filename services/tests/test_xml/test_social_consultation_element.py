from django.test import tag

from services.tests.xml_test_case import XMLTestCase
from services.xml.social_consultation_element import SocialConsultationElement
from snomedct.models import SnomedConcept, ReadCode

from model_mommy import mommy


class SocialConsultationElementTest(XMLTestCase):
    def setUp(self):
        super().setUp(SocialConsultationElement.XPATH)
        self.social_consultation_elements = [
            SocialConsultationElement(e) for e in self.elements
        ]
        smoking_readcode = mommy.make(ReadCode, ext_read_code='SMO8')
        alcohol_readcode = mommy.make(ReadCode, ext_read_code='ALC7')
        mommy.make(SnomedConcept, external_id=365981007, readcode=smoking_readcode)
        mommy.make(SnomedConcept, external_id=228273003, readcode=alcohol_readcode)

    def test_date(self):
        self.assertEqual(
            '27/08/2017',
            self.social_consultation_elements[0].date()
        )

    def test_description(self):
        self.assertEqual(
            'Non-smoker',
            self.social_consultation_elements[0].description()
        )

    def test_is_smoking_returns_false_for_non_smoker(self):
        self.assertFalse(self.social_consultation_elements[0].is_smoking())

    @tag('notimplemented')
    def test_is_smoking_from_readcode(self):
        self.assertTrue(self.social_consultation_elements[2].is_smoking())

    @tag('notimplemented')
    def test_is_smoking_from_snomed(self):
        self.assertTrue(self.social_consultation_elements[3].is_smoking())

    def test_is_alcohol_returns_false_for_non_alcohol_drinker(self):
        self.assertFalse(self.social_consultation_elements[0].is_alcohol())

    @tag('notimplemented')
    def test_is_alcohol_from_readcode(self):
        self.assertTrue(self.social_consultation_elements[4].is_alcohol())

    @tag('notimplemented')
    def test_is_alcohol_from_snomed(self):
        self.assertTrue(self.social_consultation_elements[5].is_alcohol())
