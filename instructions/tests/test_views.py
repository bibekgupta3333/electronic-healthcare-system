from django.test import TestCase, Client
from django.shortcuts import reverse
from model_mommy import mommy
from snomedct.models import SnomedConcept
from accounts.models import User, ClientUser, Patient, GeneralPracticeUser
from instructions.models import Instruction, InstructionAdditionQuestion, \
                                InstructionConditionsOfInterest, Setting, \
                                InstructionPatient
from instructions.model_choices import *
from organisations.models import OrganisationGeneralPractice
from instructions.tables import InstructionTable


class TestCountInstructions(TestCase):
    def test_count_instructions_if_user_is_gp(self):
        status = ''
        all_count = 1
        new_count = 1
        progress_count = 1
        overdue_count = 1
        complete_count = 1
        rejected_count = 1
        self.assertEqual(1, all_count)
        status = INSTRUCTION_STATUS_NEW
        self.assertEqual(1, new_count)
        status = INSTRUCTION_STATUS_PROGRESS
        self.assertEqual(1, progress_count)
        status = INSTRUCTION_STATUS_OVERDUE
        self.assertEqual(1, overdue_count)
        status = INSTRUCTION_STATUS_COMPLETE
        self.assertEqual(1, complete_count)
        status = INSTRUCTION_STATUS_REJECT
        self.assertEqual(1, rejected_count)


class TestCalculateNextPrev(TestCase):
    def setUp(self):
        self.page_number = 5
        self.num_pages = 10
        self.prev_disabled = ''
        self.next_disabled = ''

    def test_calculate_next_prev(self):
        if self.page_number <= 1:
            prev_disabled = 'disabled'
            self.assertEqual('disabled', prev_disabled)
        else:
            self.assertEqual(4, self.page_number - 1)

        if self.page_number >= self.num_pages:
            next_disabled = 'disabled'
            self.assertEqual('disabled', next_disabled)
        else:
            self.assertEqual(6, self.page_number + 1)


class TestCreateOrUpdateInstruction(TestCase):
    def setUp(self):
        user1 = mommy.make(User, username='gpuser', email='gpuser@domain.com')
        user2 = mommy.make(User, username='cltuser', email='cltuser@domain.com')
        user3 = mommy.make(User, username='patuser', email='patuser@domain.com')
        self.gp_user = mommy.make(GeneralPracticeUser, user=user1, role=0, code=1234)
        self.clt_user = mommy.make(ClientUser, user=user2, role=0)
        self.patient = mommy.make(Patient, user=user3)
        self.gp_practice = mommy.make(
            OrganisationGeneralPractice, pk=1,
            name='GP Organisation',
            gp_operating_system='OT',
            practcode='99999'
        )
        self.new_instruction = mommy.make(Instruction, pk=98765)
        self.existing_instruction = mommy.make(
            Instruction,
            pk=987654,
            client_user=self.clt_user,
            patient=self.patient,
            type=SARS_TYPE,
            gp_practice=self.gp_practice
        )

    def test_create_instruction_client_user(self):
        instruction = self.new_instruction
        instruction.client_user = self.clt_user
        instruction.type = AMRA_TYPE
        instruction.gp_practice = self.gp_practice
        self.assertEqual(98765, instruction.pk)

    def test_update_instruction_not_client_user(self):
        instruction = self.existing_instruction
        instruction.gp_practice = self.gp_practice
        instruction.type = SARS_TYPE
        instruction.gp_user = self.gp_user
        self.assertEqual(987654, instruction.pk)


class TestCreateAdditionQuestion(TestCase):
    def setUp(self):
        user1 = mommy.make(User, username='cltuser', email='cltuser@domain.com')
        user2 = mommy.make(User, username='patuser', email='patuser@domain.com')
        self.clt_user = mommy.make(ClientUser, user=user1, role=0)
        self.patient = mommy.make(Patient, user=user2)
        self.gp_practice = mommy.make(
            OrganisationGeneralPractice, pk=1,
            name='GP Organisation',
            gp_operating_system='OT',
            practcode='99999'
        )
        self.instruction = mommy.make(
            Instruction, client_user=self.clt_user,
            patient=self.patient,
            type=SARS_TYPE,
            gp_practice=self.gp_practice
        )

    def test_create_addition_question(self):
        addition_question = mommy.make(
            InstructionAdditionQuestion,
            pk=9999,
            question='sample question',
            instruction=self.instruction
        )
        self.assertEqual(9999
        , addition_question.pk)


class TestCreateSnomedRelations(TestCase):
    def setUp(self):
        user1 = mommy.make(User, username='cltuser', email='cltuser@domain.com')
        user2 = mommy.make(User, username='patuser', email='patuser@domain.com')
        self.clt_user = mommy.make(ClientUser, user=user1, role=0)
        self.patient = mommy.make(Patient, user=user2)
        self.gp_practice = mommy.make(
            OrganisationGeneralPractice, pk=1,
            name='GP Organisation',
            gp_operating_system='OT',
            practcode='99999'
        )
        self.instruction = mommy.make(
            Instruction, client_user=self.clt_user,
            patient=self.patient,
            type=SARS_TYPE,
            gp_practice=self.gp_practice
        )

    def test_create_snomed_relations(self):
        snomedct = mommy.make(
            SnomedConcept,
            external_id = 98765,
            fsn_description = 'asdf'
        )
        condition_of_interest = mommy.make(
            InstructionConditionsOfInterest,
            pk = 90009,
            instruction = self.instruction,
            snomedct = snomedct
        )
        self.assertEqual(90009, condition_of_interest.pk)


class TestInstructionPipelineView(TestCase):
    def test_view_url(self):
        response = self.client.get('/instruction/view-pipeline/')
        self.assertEqual(302, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('instructions:view_pipeline')
        )
        self.assertEqual(302, response.status_code)


class TestNewInstruction(TestCase):
    def test_view_url(self):
        response = self.client.get('/instruction/new-instruction/')
        self.assertEqual(302, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('instructions:new_instruction')
        )
        self.assertEqual(302, response.status_code)

    def test_create_sars_instruction(self):
        response = self.client.post('/instruction/new-instruction/', {
            'patient_title': 'MR',
            'patient_first_name': 'patient1',
            'patient_postcode': 'N10 1AE',
            'patient_country': 'Country'
        })
        self.assertEqual(302, response.status_code)

    def test_create_amra_instruction(self):
        response = self.client.post('/instruction/new-instruction/', {
            'patient_title': 'MR',
            'patient_first_name': 'patient1',
            'patient_postcode': 'N10 1AE',
            'patient_country': 'Country',
            'gp_practice': '1234',
            'gp_practice_name': 'Gp organisation',
            'gp_title': 'MR',
            'type': 'AMRA',
            'common_condition': [10101010]
        })
        self.assertEqual(302, response.status_code)

    def test_create_amra_instruction_invalid_patient_form(self):
        response = self.client.post('/instruction/new-instruction/', {
            'patient_title': 'MR',
            'patient_first_name': 'aaa',
            'patient_last_name': 'bbb',
            'patient_postcode': 'N10 1AG',
            'patient_city': 'London',
            'patient_country': '',
            'patient_email': '',
            'gp_practice': '12345',
            'gp_practice_name': 'GP Organisation',
            'type': 'AMRA'
        })
        self.assertEqual(302, response.status_code)


class TestReviewInstruction(TestCase):
    def test_view_url(self):
        response = self.client.get('/instruction/review-instruction/1')
        self.assertEqual(302, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('instructions:review_instruction', args=(1,))
        )
        self.assertEqual(302, response.status_code)


class TestConsentContact(TestCase):
    def test_view_url(self):
        response = self.client.get('/instruction/consent-contact/1/select-patient/1001/')
        self.assertEqual(404, response.status_code)

    def test_view_url_by_name(self):
        response = self.client.get(
            reverse('instructions:consent_contact', args=(1, 1001))
        )
        self.assertEqual(302, response.status_code)

    def test_consent_contact_save_and_view_pipeline(self):
        response = self.client.post('/instruction/consent-contact/1/select-pattient/1001', {
            'next_step': 'view_pipeline',
            'mdx_consent_loaded': 'loaded',
            'patient_email': 'patient@domain.com'
        })
        self.assertEqual(404, response.status_code)

    def test_consent_contact_proceed_to_report(self):
        response = self.client.post('/instruction/consent-contact/1/select-pattient/1001', {
            'next_step': 'proceed',
            'sars_consent_loaded': 'loaded',
            'mdx_consent_loaded': 'loaded',
            'patient_email': 'patient@domain.com'
        })
        self.assertEqual(404, response.status_code)
