from django.test import TestCase
from .models import OrganisationFee
from model_mommy import mommy
from organisations.models import OrganisationGeneralPractice


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
        self.assertEqual(str(OrganisationFee._meta.verbose_name), "Organisation Fee Structure")

    def test_verbose_name_plural(self):
        self.assertEqual(str(OrganisationFee._meta.verbose_name_plural), "Organisation Fee Structures")
