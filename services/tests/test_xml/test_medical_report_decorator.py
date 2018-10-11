from django.test import TestCase
from django.test import tag
from services.xml.medical_report_decorator import MedicalReportDecorator


@tag('notimplemented')
class MedicalReportDecoratorTest(TestCase):
    def test_consultations(self):
        self.fail('Not implemented')

    def test_significant_active_problems(self):
        self.fail('Not implemented')

    def test_significant_past_problems(self):
        self.fail('Not implemented')

    def test_referrals(self):
        self.fail('Not implemented')

    def test_attachments(self):
        self.fail('Not implemented')

    def test_acute_medications(self):
        self.fail('Not implemented')

    def test_repeat_medications(self):
        self.fail('Not implemented')

    def test_all_allergies(self):
        self.fail('Not implemented')

    def test_profile_events_for(self):
        self.fail('Not implemented')

    def test_profile_events_by_type(self):
        self.fail('Not implemented')

    def test_bloods_for(self):
        self.fail('Not implemented')

    def test_blood_test_results_by_type(self):
        self.fail('Not implemented')
