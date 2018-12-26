from django.test import TestCase
from ..models import OrganisationFee, InstructionVolumeFee
from model_mommy import mommy
from organisations.models import OrganisationGeneralPractice, OrganisationClient


class OrganisationFeeModelTest(TestCase):
    def setUp(self):
        self.gp_practice = mommy.make(
            OrganisationGeneralPractice,
            name="Test Trading Name GP Organisation"

        )

        self.organisation_fee = mommy.make(
            OrganisationFee,
            gp_practice=self.gp_practice,
            max_day_lvl_1=3,
            max_day_lvl_2=6,
            max_day_lvl_3=8,
            max_day_lvl_4=10,
            amount_rate_lvl_1=70,
            amount_rate_lvl_2=50,
            amount_rate_lvl_3=30,
            amount_rate_lvl_4=20
        )

    def test_string_representation(self):
        self.assertEqual(str(self.organisation_fee), "Fee Structure: {}".format(self.gp_practice))

    def test_verbose_name(self):
        self.assertEqual(str(OrganisationFee._meta.verbose_name), "GP Organisation Fee Structure")

    def test_verbose_name_plural(self):
        self.assertEqual(str(OrganisationFee._meta.verbose_name_plural), "GP Organisation Fee Structures")


class InstructionVolumeFeeModelTest(TestCase):

    def setUp(self):
        self.client_organisation = mommy.make(
            OrganisationClient,
            trading_name='Test Trading Name Client Organisation'
        )

        self.instruction_volume_fee = mommy.make(
            InstructionVolumeFee,
            client_organisation=self.client_organisation,
            max_volume_band_lowest=10000,
            max_volume_band_low=20000,
            max_volume_band_medium=50000,
            max_volume_band_top=100000,
            fee_rate_lowest=20,
            fee_rate_low=18,
            fee_rate_medium=15,
            fee_rate_top=10
        )

    def test_string_representation(self):
        self.assertEqual(str(self.instruction_volume_fee), "Fee Structure: {}".format(self.client_organisation))

    def test_verbose_name(self):
        self.assertEqual(str(InstructionVolumeFee._meta.verbose_name), "Client Organisation Fee structure")

    def test_verbose_name_plural(self):
        self.assertEqual(str(InstructionVolumeFee._meta.verbose_name_plural), "Client Organisation Fee structures")