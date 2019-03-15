from django.test import TestCase
from django.shortcuts import reverse
from accounts.models import User
from django.core.files import File
from unittest.mock import Mock
from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_FINALISE, INSTRUCTION_STATUS_FAIL, INSTRUCTION_STATUS_COMPLETE
from payment.models import OrganisationFeeRate


class SurgeryOnboard(TestCase):

    def setUp(self):
        self.practice_code = 'TESTSURGERY'
        self.emis_org_code = '29390'
        self.email = 'mohara@mohara.co'
        self.surgery_email = 'surgery@mohara.co'
        self.patient_email = 'patient@mohara.co'
        self.password = 'Surgery2018test'
        self.address = 'Aberdeen City Council, Director of Housing  St. Nicholas House, Broad Street, Aberdeen, Aberdeenshire'
        self.phone_number = '874432803'
        self.phone_code = '66'
        self.emis_number = '500139'
        self.patient_first_name = 'Sarah'
        self.patient_last_name = 'Giles'
        self.day_of_dob = '21'
        self.month_of_dob = '9'
        self.year_of_dob = '1962'
        self.create_fee()
        self.onboarding()
        self.emis_polling()
        self.emr_setup_final()

    def create_fee(self):
        self.fee = OrganisationFeeRate.objects.create(
            name='Surgery Fee',
            amount_rate_lvl_1=70,
            amount_rate_lvl_2=60,
            amount_rate_lvl_3=50,
            amount_rate_lvl_4=40,
            default=True
        )

    def onboarding(self):
        data = {
            'accept_policy': 'on',
            'address': self.address,
            'address_line1': 'Child Protection Partnership',
            'address_line2': 'Business Hub 2',
            'address_line3': 'Aberdeen',
            'city': 'Aberdeen',
            'consented': 'on',
            'contact_num': '29390',
            'county': 'Aberdeenshire',
            'email1': self.email,
            'email2': self.email,
            'emis_org_code': self.emis_org_code,
            'first_name': 'Surgery',
            'operating_system': 'EMISWeb',
            'password1': self.password,
            'password2': self.password,
            'postcode': 'AB10 1AF',
            'practice_code': self.practice_code,
            'surgery_name': 'TESTSURGERY',
            'surname': 'Medi',
            'telephone_code': self.phone_code,
            'telephone_mobile': self.phone_number,
            'title': 'MR'
        }
        response = self.client.post(reverse('onboarding:sign_up'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/onboarding/emis-setup/' + self.practice_code)

    def emis_polling(self):
        response = self.client.get(reverse('onboarding:emis_polling', kwargs={'practice_code':self.practice_code}))
        result = {'status': 400, 'practice_code': self.practice_code}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), result)
        self.user = User.objects.get(email=self.email)
        self.client.force_login(self.user)

    def emr_setup_final(self):
        data = {
            'completed_by': 'Surgery',
            'confirm_email': self.surgery_email,
            'form-0-email': 'manager@mohara.co',
            'form-0-first_name': 'Manager',
            'form-0-last_name': 'GP',
            'form-0-mobile_code': self.phone_code,
            'form-0-mobile_phone': self.phone_number,
            'form-0-role': '0',
            'form-0-title': 'MR',
            'form-1-email': 'gp@mohara.co',
            'form-1-first_name': 'GP',
            'form-1-last_name': 'GP',
            'form-1-mobile_code': self.phone_code,
            'form-1-mobile_phone': self.phone_number,
            'form-1-role': '1',
            'form-1-title': 'MR',
            'form-2-email': 'other@mohara.co',
            'form-2-first_name': 'Other',
            'form-2-last_name': 'GP',
            'form-2-mobile_code': self.phone_code,
            'form-2-mobile_phone': self.phone_number,
            'form-2-role': '2',
            'form-2-title': 'MR',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-MIN_NUM_FORMS': '0',
            'form-TOTAL_FORMS': '3',
            'job_title': 'Surgery',
            'bank_account_name': 'SURGERY',
            'bank_account_number': '1234567890',
            'bank_account_sort_code': '1234567890',
            'received_after_11_days': '40',
            'received_within_8_to_11_days': '50',
            'received_within_4_to_7_days': '60',
            'received_within_3_days': self.fee.pk,
            'organisation_email': self.surgery_email
        }
        response = self.client.post(reverse('onboarding:emr_setup_final', kwargs={'practice_code':self.practice_code}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/onboarding/emis-setup-success/')


class SurgerySARSFlow(SurgeryOnboard):

    def setUp(self):
        super().setUp()
        self.create_sars()
        self.add_consent_contact()
        self.preview_report()
        self.submit_report()

    def create_sars(self):
        data = {
            'date_range_from': '',
            'date_range_to': '',
            'instruction_id': '',
            'patient_address_line1': 'Aberdeen City Council',
            'patient_address_line2': ' Finance Department  Town House',
            'patient_address_line3': ' Broad Street',
            'patient_address_number': self.address,
            'patient_city': ' Aberdeen',
            'patient_county': ' Aberdeenshire',
            'patient_dob_day': self.day_of_dob,
            'patient_dob_month': self.month_of_dob,
            'patient_dob_year': self.year_of_dob,
            'patient_first_name': self.patient_first_name,
            'patient_last_name': self.patient_last_name,
            'patient_nhs_number': '',
            'patient_postcode': 'AB10 1AH',
            'patient_title': 'MIS'
        }
        response = self.client.post(reverse('instructions:new_instruction'), data)
        self.instruction = Instruction.objects.filter(gp_user__user__pk=self.user.pk).first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/medicalreport/' + str(self.instruction.pk) + '/patient-emis-number/')

    def add_consent_contact(self):
        mock_mdx_file = Mock(spec=File)
        data = {
            'confirm_email': self.patient_email,
            'mdx_consent_loaded': 'loaded',
            'mdx_consent': mock_mdx_file,
            'next_step': 'proceed',
            'patient_address_number': self.address,
            'patient_alternate_code': self.phone_code,
            'patient_alternate_phone': self.phone_number,
            'patient_dob': '/'.join([self.day_of_dob,self.month_of_dob,self.year_of_dob]),
            'patient_email': self.patient_email,
            'patient_first_name': self.patient_first_name,
            'patient_last_name': self.patient_last_name,
            'patient_nhs_number': '',
            'patient_postcode': 'AB10 1AF',
            'patient_telephone_code': self.phone_code,
            'patient_telephone_mobile': self.phone_number,
            'patient_title': 'Mr.',
            'sars_consent': '',
            'sars_consent_loaded': ''
        }
        response = self.client.post(reverse(
            'instructions:consent_contact',
            kwargs={'instruction_id':self.instruction.pk, 'patient_emis_number':self.emis_number})
        , data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/medicalreport/' + str(self.instruction.pk) + '/select-patient/' + self.emis_number + '/')
        response = self.client.get(reverse(
            'medicalreport:select_patient',
            kwargs={'instruction_id':self.instruction.pk, 'patient_emis_number':self.emis_number})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/medicalreport/' + str(self.instruction.pk) + '/edit/')

    def preview_report(self):
        data = {
            'additional_allergies_allergen': '',
            'additional_allergies_date_discovered': '',
            'additional_allergies_reaction': '',
            'additional_medication_dose': '',
            'additional_medication_drug': '',
            'additional_medication_frequency': '',
            'additional_medication_notes': '',
            'additional_medication_prescribed_from': '',
            'additional_medication_prescribed_to': '',
            'additional_medication_records_type': '',
            'additional_medication_related_condition': '',
            'event_flag': 'preview',
            'redaction_acute_prescription_notes': '',
            'redaction_attachment_notes': '',
            'redaction_bloods_notes': '',
            'redaction_comment_notes': '',
            'redaction_consultation_notes': '',
            'redaction_referral_notes': '',
            'redaction_repeat_prescription_notes': '',
            'redaction_significant_problem_notes': '',
            'redaction_xpaths': None
        }
        response = self.client.post(reverse('medicalreport:update_report', kwargs={'instruction_id':self.instruction.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/medicalreport/' + str(self.instruction.pk) + '/submit-report/')

    def submit_report(self):
        data = {
            'event_flag': 'submit',
            'prepared_and_signed': 'PREPARED_AND_REVIEWED',
            'prepared_by': '1'
        }
        response = self.client.post(reverse('medicalreport:update_report', kwargs={'instruction_id':self.instruction.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/instruction/view-pipeline/')

    def test_instruction_files(self):
        instruction = Instruction.objects.get(pk=self.instruction.pk)
        if not instruction.medical_report:
            self.fail("Medical report is missing")
        if not instruction.medical_xml_report:
            self.fail("Medical report xml is missing")
        if instruction.status not in [INSTRUCTION_STATUS_FINALISE, INSTRUCTION_STATUS_FAIL, INSTRUCTION_STATUS_COMPLETE]:
            self.fail("Instruction invalid status")
