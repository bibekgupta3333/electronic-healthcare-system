from django.test import TestCase
from django.test import tag

@tag('notimplemented')
class RedactionTest(TestCase):
    def test_additional_acute_medications(self):
        self.fail('Not implemented')

    def test_additional_repeat_medications(self):
        self.fail('Not implemented')

    def test_additional_allergies(self):
        self.fail('Not implemented')

    def test_redacted(self):
        self.fail('Not implemented')
