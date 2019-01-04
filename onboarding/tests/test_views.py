from django.test import TestCase, Client

from model_mommy import mommy

from organisations.models import OrganisationGeneralPractice
from accounts.models import GeneralPracticeUser, User, GENERAL_PRACTICE_USER


class OnboardingHackingURLTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_gp_practice = mommy.make(OrganisationGeneralPractice, practcode='GP0002', live=True, accept_policy=True)
        self.active_user = mommy.make(User, email='activeuser@testmail.com', password='test1234', type=GENERAL_PRACTICE_USER)
        self.active_practice_manager = mommy.make(GeneralPracticeUser, user=self.active_user, organisation=self.active_gp_practice)
        self.inactice_gp_practice = mommy.make(OrganisationGeneralPractice, practcode='GP0001', live=False)
        self.inactive_user = mommy.make(User, email='inactiveuser@testmail.com', password='test1234', type=GENERAL_PRACTICE_USER)
        self.practice_manager = mommy.make(GeneralPracticeUser, user=self.inactive_user, organisation=self.inactice_gp_practice)

    def test_logged_in_hacking_emis_setup_views(self):
        self.client.force_login(self.active_user)
        response = self.client.get('/onboarding/emis-setup/GP0001')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/accounts/login/', response.url)
        self.client.logout()

    def test_logged_in_hacking_emr_setup_final_views(self):
        self.client.force_login(self.active_user)
        response = self.client.get('/onboarding/emr-setup-final/GP0001')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/accounts/login/', response.url)
        self.client.logout()

    def test_non_logged_in_hacking_emis_setu_views(self):
        response = self.client.get('/onboarding/emis-setup/GP0001')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/accounts/login?next=/onboarding/emis-setup/GP0001', response.url)

    def test_non_logged_in_hacking_emr_setup_final_views(self):
        response = self.client.get('/onboarding/emr-setup-final/GP0001')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/accounts/login?next=/onboarding/emr-setup-final/GP0001', response.url)

    def test_non_active_user_redirect_from_pipeline_views_to_emis_setup(self):
        self.client.force_login(self.inactive_user)
        response = self.client.get('/instruction/view-pipeline/')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/onboarding/emis-setup/GP0001', response.url)
        self.client.logout()

    def test_success_access_emis_setup_views(self):
        self.client.force_login(self.inactive_user)
        response = self.client.get('/onboarding/emis-setup/GP0001')
        self.assertEqual(200, response.status_code)
        self.client.logout()

    def test_success_access_emr_setup_final_views(self):
        self.client.force_login(self.inactive_user)
        response = self.client.get('/onboarding/emr-setup-final/GP0001')
        self.assertEqual(200, response.status_code)
        self.client.logout()
