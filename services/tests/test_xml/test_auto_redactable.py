from django.test import tag

from services.tests.xml_test_case import XMLTestCase
from services.xml.auto_redactable import (
    years_ago, auto_redact_by_conditions, auto_redact_consultations,
    auto_redact_medications, auto_redact_referrals, auto_redact_attachments,
    auto_redact_profile_events
)
from services.xml.attachment import Attachment
from services.xml.consultation import Consultation
from services.xml.medication import Medication
from services.xml.referral import Referral
from services.xml.value_event import ValueEvent

from instructions.models import Instruction, InstructionConditionsOfInterest
from snomedct.models import SnomedConcept, ReadCode

from model_mommy import mommy

from datetime import date


class AutoRedactableTest(XMLTestCase):
    def setUp(self):
        super().setUp()
        medication_elements = self.parsed_xml.xpath(Medication.XPATH)
        self.medications = [Medication(e) for e in medication_elements]
        self.instruction = mommy.make(Instruction)
        snomed_ct_1 = mommy.make(
            SnomedConcept, external_id=90332006)
        snomed_ct_2 = mommy.make(
            SnomedConcept, external_id=1331000000103)
        mommy.make(ReadCode, ext_read_code='1371.', concept_id=snomed_ct_1)
        mommy.make(ReadCode, ext_read_code='9D11.', concept_id=snomed_ct_2)
        mommy.make(
            InstructionConditionsOfInterest, instruction=self.instruction,
            snomedct=snomed_ct_1
        )
        mommy.make(
            InstructionConditionsOfInterest, instruction=self.instruction,
            snomedct=snomed_ct_2
        )

    def test_years_ago(self):
        test_date_1 = date(year=2016, month=2, day=29)
        test_date_2 = date(year=2018, month=10, day=1)
        test_date_3 = date(year=2017, month=2, day=28)
        expected_date_1 = date(year=2015, month=2, day=28)
        expected_date_2 = date(year=2017, month=10, day=1)
        expected_date_3 = date(year=2016, month=2, day=28)
        self.assertEqual(expected_date_1, years_ago(1, test_date_1))
        self.assertEqual(expected_date_2, years_ago(1, test_date_2))
        self.assertEqual(expected_date_3, years_ago(1, test_date_3))

    def test_auto_redact_by_conditions(self):
        self.assertEqual(4, len(self.medications))
        self.assertEqual(
            1,
            len(auto_redact_by_conditions(self.medications, self.instruction))
        )

    def test_auto_redact_by_date(self):
        self.test_auto_redact_referrals()

    def test_auto_redact_consultations(self):
        consultation_elements = self.parsed_xml.xpath(Consultation.XPATH)
        consultations = [Consultation(e) for e in consultation_elements]
        self.assertEqual(9, len(consultations))
        test_date = date(2018, 1, 1)
        self.assertEqual(
            2,
            len(auto_redact_consultations(
                consultations, self.instruction, test_date))
        )

    def test_auto_redact_medications(self):
        test_date = date(2018, 1, 1)
        self.assertEqual(4, len(self.medications))
        self.assertEqual(
            3,
            len(auto_redact_medications(self.medications, test_date))
        )

    def test_auto_redact_referrals(self):
        referral_elements = self.parsed_xml.xpath(Referral.XPATH)
        referrals = [Referral(e) for e in referral_elements]
        test_date = date(2022, 1, 1)
        self.assertEqual(1, len(referrals))
        self.assertEqual(
            0,
            len(auto_redact_referrals(referrals, test_date))
        )

    def test_auto_redact_attachments(self):
        attachment_elements = self.parsed_xml.xpath(Attachment.XPATH)
        attachments = [Attachment(e) for e in attachment_elements]
        test_date = date(2019, 1, 1)
        self.assertEqual(3, len(attachments))
        self.assertEqual(
            2,
            len(auto_redact_attachments(attachments, test_date))
        )

    def test_auto_redact_profile_events(self):
        value_event_elements = self.parsed_xml.xpath(ValueEvent.XPATH)
        value_events = [ValueEvent(e) for e in value_event_elements]
        test_date = date(2020, 1, 1)
        self.assertEqual(21, len(value_events))
        self.assertEqual(
            12,
            len(auto_redact_profile_events(value_events, test_date))
        )
