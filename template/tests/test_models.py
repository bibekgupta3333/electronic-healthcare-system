from django.test import TestCase

from model_mommy import mommy

from template.models import (
    TemplateInstruction, TemplateInstructionAdditionalQuestion
)


class TemplateInstructionTest(TestCase):
    def test_string_representation(self):
        template_instruction = mommy.make(
            TemplateInstruction, template_title='template_instruction'
        )
        self.assertEqual(str(template_instruction), 'template_instruction')


class TemplateInstructionAdditionalQuestionTest(TestCase):
    def test_string_representation(self):
        template_instruction_additional_question = mommy.make(
            TemplateInstructionAdditionalQuestion, question='test_question?'
        )
        self.assertEqual(
            str(template_instruction_additional_question), 'test_question?'
        )
