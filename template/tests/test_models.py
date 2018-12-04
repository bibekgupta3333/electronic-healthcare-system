from django.test import TestCase

from model_mommy import mommy

from template.models import (
    TemplateInstruction, TemplateAdditionalQuestion
)


class TemplateInstructionTest(TestCase):
    def test_string_representation(self):
        template_instruction = mommy.make(
            TemplateInstruction, template_title='template_instruction'
        )
        self.assertEqual(str(template_instruction), 'template_instruction')


class TemplateAdditionalQuestionTest(TestCase):
    def test_string_representation(self):
        template_additional_question = mommy.make(
            TemplateAdditionalQuestion, question='test_question?'
        )
        self.assertEqual(
            str(template_additional_question), 'test_question?'
        )
