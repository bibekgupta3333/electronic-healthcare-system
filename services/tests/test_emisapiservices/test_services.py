from datetime import date
from django.test import TestCase

from model_mommy import mommy

from services.emisapiservices.services import (
    EmisAPIServiceBase, GetAttachment, GetPatientList, GetMedicalRecord
)
from services.models import EmisAPIConfig
from instructions.models import InstructionPatient
from medicalreport.tests.test_views import EmisAPITestCase

from django.conf import settings
EMIS_API_HOST = settings.EMIS_API_HOST


def generate_emis_api_config():
    mommy.make(
        EmisAPIConfig, emis_organisation_id='emis_id',
        emis_username='emis_username', emis_password=''
    )


class EmisAPIServiceBaseTest(TestCase):
    def setUp(self):
        generate_emis_api_config()
        self.emis_api_service_base = EmisAPIServiceBase()

    def test_uri_raises_error(self):
        self.assertRaises(NotImplementedError, self.emis_api_service_base.uri)


class GetAttachmentTest(TestCase):
    def setUp(self):
        generate_emis_api_config()
        self.get_attachment = GetAttachment(
            patient_number='P123', attachment_identifier='attachment id', gp_organisation=None
        )

    def test_uri(self):
        expected = f'{EMIS_API_HOST}/api/organisations/emis_id/patients/P123/attachments/attachment%20id'
        self.assertEqual(self.get_attachment.uri(), expected)


class GetPatientListTest():
    def setUp(self):
        generate_emis_api_config()
        patient = mommy.make(
            InstructionPatient,
            patient_first_name='first_name',
            patient_last_name='last_name',
            patient_dob=date(1990, 1, 2)
        )
        self.get_patient_list = GetPatientList(patient, gp_organisation=None)
        blank_patient = mommy.make(
            InstructionPatient,
            patient_first_name='',
            patient_last_name='',
            patient_dob=None
        )
        self.get_patient_list_blank = GetPatientList(blank_patient, gp_organisation=None)

    def test_search_term(self):
        self.assertEqual(
            self.get_patient_list.search_term(),
            'first_name%20last_name%2002%2F01%2F1990'
        )

    def test_search_term_with_blank_fields(self):
        self.assertEqual(self.get_patient_list_blank.search_term(), '')

    def test_uri(self):
        expected = f'{EMIS_API_HOST}/api/organisations/emis_id/patients?q=first_name%20last_name%2002%2F01%2F1990'
        self.assertEqual(self.get_patient_list.uri(), expected)


class GetMedicalRecordTest(EmisAPITestCase):
    def setUp(self):
        generate_emis_api_config()
        self.get_medical_record = GetMedicalRecord(patient_number='P123', gp_organisation=None)

    def test_uri(self):
        expected = f'{EMIS_API_HOST}/api/organisations/emis_id/patients/P123/medical_record'
        self.assertEqual(self.get_medical_record.uri(), expected)
