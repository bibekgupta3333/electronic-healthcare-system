from django.test import TestCase
from django.http import JsonResponse
from django.shortcuts import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from model_mommy import mommy

from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_REJECT, INSTRUCTION_STATUS_PROGRESS,\
    INSTRUCTION_STATUS_COMPLETE, INSTRUCTION_STATUS_NEW
from accounts.models import ClientUser, User, GeneralPracticeUser, Patient, GENERAL_PRACTICE_USER, CLIENT_USER
from services.models import EmisAPIConfig
from medicalreport.models import AmendmentsForRecord
from medicalreport.views import get_matched_patient, get_patient_record
from organisations.models import OrganisationGeneralPractice

import os
from contextlib import suppress


class EmisAPITestCase(TestCase):
    def setUp(self):
        EmisAPIConfig.objects.create(
            emis_organisation_id='29390',
            emis_username='michaeljtbrooks',
            emis_password='Medidata2018'
        )
        patient_user = mommy.make(
            User, first_name='Alan', last_name='Ball')
        self.patient = mommy.make(
            Patient, user=patient_user, emis_number='2985', date_of_birth=None)
        user = mommy.make(User, type=GENERAL_PRACTICE_USER)
        gp_practice = mommy.make(
            OrganisationGeneralPractice, pk=1,
            trading_name='GP Organisation', legal_name='GP',
            address='99/99 Bangkok 2510', operating_system='OT',
            practice_code='99999'
        )
        self.gp_user = mommy.make(GeneralPracticeUser, user=user, organisation=gp_practice)
        self.gp_practice = gp_practice
        consent_form = SimpleUploadedFile('test_consent_form.txt', b'consent')
        self.instruction = mommy.make(
            Instruction, pk=1, consent_form=consent_form,
            patient=self.patient, gp_user=self.gp_user,
            gp_practice=gp_practice
        )
        self.redaction = mommy.make(
            AmendmentsForRecord, instruction=self.instruction, pk=1
        )
        self.client.force_login(user, backend=None)

    def tearDown(self):
        with suppress(FileNotFoundError, AttributeError, ValueError):
            os.remove(self.instruction.consent_form.path)


class GetMatchedPatientTest(EmisAPITestCase):
    def test_get_matched_patient(self):
        registrations = get_matched_patient(self.patient)
        self.assertIn(
            'Mr Alan Ball',
            [registration.full_name() for registration in registrations]
        )


class RejectRequestTest(EmisAPITestCase):
    def setUp(self):
        super().setUp()
        consent_form = SimpleUploadedFile('test_consent_form.txt', b'consent')
        self.instruction = mommy.make(
            Instruction, pk=4, consent_form=consent_form,
            patient=self.patient, gp_user=self.gp_user,
            gp_practice=self.gp_practice, status=INSTRUCTION_STATUS_REJECT
        )
        self.redaction = mommy.make(
            AmendmentsForRecord, instruction=self.instruction, pk=4
        )

    def test_view_url(self):
        response = self.client.post('/medicalreport/4/reject-request/')
        self.assertEqual(302, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.post(
            reverse('medicalreport:reject_request', args=(4,))
        )
        self.assertEqual(302, response.status_code)

    def test_view_redirects_to_correct_url(self):
        response = self.client.post('/medicalreport/4/reject-request/')
        self.assertRedirects(response, '/instruction/view-pipeline/?status=%s&type=allType'%INSTRUCTION_STATUS_REJECT)


class SelectPatientTest(EmisAPITestCase):
    def test_view_url(self):
        response = self.client.get('/medicalreport/1/select-patient/2985/')
        self.assertEqual(302, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('medicalreport:select_patient', args=(1, 2985))
        )
        self.assertEqual(302, response.status_code)

    def test_view_redirects_to_correct_url(self):
        response = self.client.get('/medicalreport/1/select-patient/2985/')
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, '/medicalreport/1/edit/')

    def test_instruction_status_is_set(self):
        self.assertNotEqual(INSTRUCTION_STATUS_PROGRESS, self.instruction.status)
        self.client.get('/medicalreport/1/select-patient/2985/')
        self.instruction.refresh_from_db()
        self.assertEqual(INSTRUCTION_STATUS_PROGRESS, self.instruction.status)

    def test_instruction_gp_user_is_set(self):
        self.instruction.gp_user = None
        self.instruction.save()
        self.client.get('/medicalreport/1/select-patient/2985/')
        self.instruction.refresh_from_db()
        self.assertEqual(self.gp_user, self.instruction.gp_user)

    def test_new_redaction_is_created(self):
        self.redaction.delete()
        self.assertEqual(0, AmendmentsForRecord.objects.count())
        self.client.get('/medicalreport/1/select-patient/2985/')
        self.assertEqual(1, AmendmentsForRecord.objects.count())

    def test_existing_redaction_is_used(self):
        self.assertEqual(1, AmendmentsForRecord.objects.count())
        self.client.get('/medicalreport/1/select-patient/2985/')
        self.assertEqual(1, AmendmentsForRecord.objects.count())

    def test_patient_emis_number_is_set_on_redaction(self):
        self.client.get('/medicalreport/1/select-patient/2985/')
        redaction = AmendmentsForRecord.objects.get()
        self.assertEqual('2985', redaction.patient_emis_number)

    def test_view_returns_302_if_gp_user_not_found(self):
        self.client.logout()
        response = self.client.get('/medicalreport/1/select-patient/2985/')
        self.assertEqual(302, response.status_code)


class SetPatientEmisNumberTest(EmisAPITestCase):
    def test_view_url(self):
        response = self.client.get('/medicalreport/1/patient-emis-number/')
        self.assertEqual(200, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('medicalreport:set_patient_emis_number', args=(1,))
        )
        self.assertEqual(200, response.status_code)

    def test_view_uses_correct_template(self):
        response = self.client.get('/medicalreport/1/patient-emis-number/')
        self.assertTemplateUsed(
            response, 'medicalreport/patient_emis_number.html')


class EditReportTest(EmisAPITestCase):
    def setUp(self):
        super().setUp()
        consent_form = SimpleUploadedFile('test_consent_form.txt', b'consent')
        self.instruction = mommy.make(
            Instruction, pk=2, consent_form=consent_form,
            patient=self.patient, gp_user=self.gp_user,
            gp_practice=self.gp_practice, status=INSTRUCTION_STATUS_PROGRESS
        )
        self.redaction = mommy.make(
            AmendmentsForRecord, instruction=self.instruction, pk=2
        )

    def test_view_url(self):
        response = self.client.get('/medicalreport/2/edit/')
        self.assertEqual(200, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('medicalreport:edit_report', args=(2,))
        )
        self.assertEqual(200, response.status_code)

    def test_view_uses_correct_template(self):
        response = self.client.get('/medicalreport/2/edit/')
        self.assertTemplateUsed(
            response, 'medicalreport/medicalreport_edit.html')

    def test_view_returns_404_if_instruction_does_not_exist(self):
        response = self.client.get('/medicalreport/5/edit/')
        self.assertEqual(404, response.status_code)

    def test_view_redirects_if_redaction_does_not_exist(self):
        self.redaction.delete()
        response = self.client.get('/medicalreport/2/edit/')
        self.assertEqual(302, response.status_code)


class UpdateReportTest(EmisAPITestCase):
    def test_view_url(self):
        response = self.client.get('/medicalreport/1/update/')
        self.assertEqual(302, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('medicalreport:update_report', args=(1,))
        )
        self.assertEqual(302, response.status_code)

    def test_view_returns_json_response_if_request_is_ajax(self):
        response = self.client.get(
            '/medicalreport/1/update/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response, JsonResponse)

    def test_view_returns_404_if_instruction_does_not_exist(self):
        response = self.client.get('/medicalreport/2/update/')
        self.assertEqual(404, response.status_code)

    def test_view_redirects_to_correct_url_if_not_valid(self):
        response = self.client.get('/medicalreport/1/update/')
        self.assertEqual(response.url, '/medicalreport/1/edit/')

    def test_view_redirects_to_correct_url_if_event_flag_is_not_submit(self):
        response = self.client.get('/medicalreport/1/update/')
        self.assertEqual(response.url, '/medicalreport/1/edit/')

    def test_view_redirects_to_correct_url_if_event_flag_is_submit_and_is_valid(self):
        response = self.client.post('/medicalreport/1/update/', {
            'event_flag': 'submit',
            'gp_practitioner': self.gp_user.user.get_query_set_within_organisation()[0].id,
            'prepared_and_signed': 'PREPARED_AND_REVIEWED',
            'prepared_by': 'test_reviewer'
        })
        self.assertEqual(response.url, '/instruction/view-pipeline/')

    def test_view_adds_error_message_and_redirects_to_correct_url_if_no_consent_form(self):
        os.remove(self.instruction.consent_form.path)
        self.instruction.consent_form = None
        self.instruction.save()
        response = self.client.get('/medicalreport/1/update/', follow=True)
        self.assertEquals(
            "You do not have a consent form",
            list(response.context.get('messages'))[0].message
        )


class ViewReportTest(EmisAPITestCase):
    def test_view_url(self):
        response = self.client.get('/medicalreport/1/view-report/')
        self.assertEqual(200, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('medicalreport:view_report', args=(1,))
        )
        self.assertEqual(200, response.status_code)

    def test_view_returns_404_if_redaction_does_not_exist(self):
        response = self.client.get('/medicalreport/2/view-report/')
        self.assertEqual(404, response.status_code)

    def test_view_returns_pdf(self):
        response = self.client.get('/medicalreport/1/view-report/')
        self.assertEqual('application/pdf', response.get('Content-Type'))


class FinalReportTest(EmisAPITestCase):
    def setUp(self):
        super().setUp()
        consent_form = SimpleUploadedFile('test_consent_form.txt', b'consent')
        self.instruction = mommy.make(
            Instruction, pk=3, consent_form=consent_form,
            patient=self.patient, gp_user=self.gp_user,
            gp_practice=self.gp_practice, status=INSTRUCTION_STATUS_COMPLETE
        )
        self.redaction = mommy.make(
            AmendmentsForRecord, instruction=self.instruction, pk=3
        )

    def test_view_url(self):
        response = self.client.get('/medicalreport/3/final-report/')
        self.assertEqual(200, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('medicalreport:final_report', args=(3,))
        )
        self.assertEqual(200, response.status_code)

    def test_view_uses_correct_template(self):
        response = self.client.get('/medicalreport/3/final-report/')
        self.assertTemplateUsed(response, 'medicalreport/final_report.html')

    def test_view_returns_404_if_instruction_does_not_exist(self):
        response = self.client.get('/medicalreport/5/final-report/')
        self.assertEqual(404, response.status_code)
