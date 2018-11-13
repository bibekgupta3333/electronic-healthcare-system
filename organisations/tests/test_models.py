from django.test import TestCase

from model_mommy import mommy

from organisations.models import (
    OrganisationMedidata, OrganisationBase, OrganisationClient,
    OrganisationGeneralPractice, NHSGeneralPractice
)


class OrganisationMedidataTest(TestCase):
    def test_string_representation(self):
        organisation_medidata = mommy.make(
            OrganisationMedidata, trading_name='trading_name'
        )
        self.assertEqual(str(organisation_medidata), 'trading_name')


class OrganisationBaseTest(TestCase):
    def test_string_representation(self):
        organisation_base = mommy.make(
            OrganisationBase, trading_name='trading_name'
        )
        self.assertEqual(str(organisation_base), 'trading_name')


class OrganisationClientTest(TestCase):
    def test_string_representation(self):
        organisation_client = mommy.make(
            OrganisationClient, trading_name='trading_name'
        )
        self.assertEqual(str(organisation_client), 'trading_name')


class OrganisationGeneralPracticeTest(TestCase):
    def test_string_representation(self):
        organisation_general_practice = mommy.make(
            OrganisationGeneralPractice, name='trading_name'
        )
        self.assertEqual(str(organisation_general_practice), 'trading_name')


class NHSGeneralPracticeTest(TestCase):
    def test_string_representation(self):
        nhs_gp_practice = mommy.make(
            NHSGeneralPractice, name='nhs_gp_practice_name'
        )
        self.assertEqual(str(nhs_gp_practice), 'nhs_gp_practice_name')
