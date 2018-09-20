from django.test import TestCase
from .models import OrganisationFee
from organisations.models import OrganisationGeneralPractice


class OrganisationFeeModelTest(TestCase):
    def setUp(self):
        self.gp_practice = OrganisationGeneralPractice.objects.create(
            trading_name="Test Trading Name GP Organisation",
            legal_name="Test Legal Name GP Organisation",
            address="Test address",
            operating_system="EW",
            operating_system_socket_endpoint="Socket Endpoint",
            operating_system_auth_token="Auth Token",
            practice_code="CODE1234",
            payment_timing="AR",
            payment_bank_holder_name="Holder Name",
            payment_bank_sort_code="Sort Code",
            payment_bank_account_number="123456",
            payment_preference="Reference"
        )

        self.organisation_fee = OrganisationFee.objects.create(
            gp_practice=self.gp_practice,
            max_day_lvl_1=3,
            max_day_lvl_2=6,
            max_day_lvl_3=8,
            amount_rate_lvl_1=70,
            amount_rate_lvl_2=50,
            amount_rate_lvl_3=30
        )

    def test_string_representation(self):
        self.assertEqual(str(self.organisation_fee), "Fee Structure: {}".format(self.gp_practice))

    def test_verbose_name(self):
        self.assertEqual(str(OrganisationFee._meta.verbose_name), "Organisation Fee Structure")

    def test_verbose_name_plural(self):
        self.assertEqual(str(OrganisationFee._meta.verbose_name_plural), "Organisation Fee Strcutures")
