from django.test import TestCase
from django.test import tag

from model_mommy import mommy

from instructions.models import (
    Instruction, InstructionAdditionQuestion, InstructionConditionsOfInterest
)
from accounts.models import User, ClientUser, Patient
from snomedct.models import SnomedConcept


class InstructionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = mommy.make(User, username='test_user_1', first_name='client')
        user_2 = mommy.make(User, username='test_user_2', first_name='patient')
        client_user = mommy.make(ClientUser, user=user_1)
        patient = mommy.make(Patient, user=user_2)
        cls.instruction = mommy.make(
            Instruction, client_user=client_user, patient=patient
        )

    def test_string_representation(self):
        instruction_string = str(self.instruction)
        self.assertEqual(instruction_string, 'Instruction #3')

    @tag('notimplemented')
    def test_snomed_concepts_readcodes(self):
        self.fail('Not implemented')

    @tag('notimplemented')
    def test_selected_snomed_concepts(self):
        self.fail('Not implemented')


class InstructionAdditionQuestionTest(TestCase):
    def test_string_representation(self):
        instruction_addition_question = mommy.make(
            InstructionAdditionQuestion, question='test_question?'
        )
        self.assertEqual(str(instruction_addition_question), 'test_question?')


class InstructionConditionsOfInterestTest(TestCase):
    def test_string_representation(self):
        snomedct = mommy.make(
            SnomedConcept, fsn_description='fsn_description',
            external_id=1234567890
        )
        instruction_conditions_of_interest = mommy.make(
            InstructionConditionsOfInterest, snomedct=snomedct
        )
        self.assertEqual(
            str(instruction_conditions_of_interest),
            'fsn_description (1234567890)'
        )
