from django.test import TestCase
from .models import User, ClientUser, GeneralPracticeUser, MedidataUser
from .models import CLIENT_USER, GENERAL_PRACTICE_USER, MEDIDATA_USER
from organisations.models import OrganisationClient, OrganisationMedidata, OrganisationGeneralPractice


class UserTestCase(TestCase):
    def setUp(self):
        # create organisation three types [Medidata, GP, Client]
        self.claim_organisation = OrganisationClient.objects.create(
            trading_name='Claim Organisation',
            legal_name='Claim Organisation',
            address='1, My Street, Kingston, New York 12401 United States',
            type=OrganisationClient.INSURANCE_CLAIM
        )

        self.underwriter_organisation = OrganisationClient.objects.create(
            trading_name='Underwriter Organisation',
            legal_name='Underwriter Organisation',
            address='2, My Street, Kingston, New York 12401 United States',
            type=OrganisationClient.INSURANCE_CLAIM
        )

        self.medidata_organisation = OrganisationMedidata.objects.create(
            trading_name='Medidata Organisation',
            legal_name='Medidata Organisation',
            address='3 Western Road Brighton East Sussex England BN1 2NW'
        )
        self.gp_organisation = OrganisationGeneralPractice.objects.create(
            trading_name='GP Organisation',
            legal_name='GP Organisation',
            address='4, My Street, Bigtown BG23 4YZ England'
        )

        # create user
        self.claim_user_admin = User.objects._create_user(email='claim_user1@mohara.co', username='claim_user1', password='medi2018', is_staff=True, type=CLIENT_USER)
        self.claim_user2 = User.objects._create_user(email='claim_user2@mohara.co', username='claim_user2', password='medi2018', type=CLIENT_USER)
        self.claim_user3 = User.objects._create_user(email='claim_user3@mohara.co', username='claim_user3', password='medi2018', type=CLIENT_USER)
        self.underwriter_user_admin = User.objects._create_user(email='underwriter_user1@mohara.co', username='underwriter_user1', password='medi2018', is_staff=True, type=CLIENT_USER)
        self.underwriter_user2 = User.objects._create_user(email='underwriter_user2@mohara.co', username='underwriter_user2', password='medi2018', type=CLIENT_USER)
        self.gp_user_admin = User.objects._create_user(email='gp_user1@mohara.co', username='gp_user1', password='medi2018', is_staff=True, type=GENERAL_PRACTICE_USER)
        self.gp_user2 = User.objects._create_user(email='gp_user2@mohara.co', username='gp_user2', password='medi2018', type=GENERAL_PRACTICE_USER)
        self.medidata_user1 = User.objects._create_user(email='medidata_user1@mohara.co', username='medidata_user1', password='medi2018', type=MEDIDATA_USER)
        self.medidata_user2 = User.objects._create_user(email='medidata_user2@mohara.co', username='medidata_user2', password='medi2018', type=MEDIDATA_USER)

        # create claim organisation's user
        ClientUser.objects.create(user=self.claim_user_admin, organisation=self.claim_organisation)
        ClientUser.objects.create(user=self.claim_user2, organisation=self.claim_organisation)
        ClientUser.objects.create(user=self.claim_user3, organisation=self.claim_organisation)

        # create underwriter organisation's user
        ClientUser.objects.create(user=self.underwriter_user_admin, organisation=self.underwriter_organisation)
        ClientUser.objects.create(user=self.underwriter_user2, organisation=self.underwriter_organisation)

        # create gp organisation's user
        GeneralPracticeUser.objects.create(user=self.gp_user_admin, organisation=self.gp_organisation)
        GeneralPracticeUser.objects.create(user=self.gp_user2, organisation=self.gp_organisation)

        # create medidata organisation's user
        MedidataUser.objects.create(user=self.medidata_user1, organisation=self.medidata_organisation)
        MedidataUser.objects.create(user=self.medidata_user2, organisation=self.medidata_organisation)

    def test_get_user_within_organisation(self):
        # check all getting claim user's organisation must be claim_organisation
        for user in self.claim_user_admin.get_query_set_within_organisation():
            self.assertEqual(self.claim_organisation, user.userprofilebase.clientuser.organisation)

        # check all getting underwriter user's organisation must be underwriter_organisation
        for user in self.underwriter_user_admin.get_query_set_within_organisation():
            self.assertEqual(self.underwriter_organisation, user.userprofilebase.clientuser.organisation)

        # check all getting gp user's organisation must be gp_organisation
        for user in self.gp_user_admin.get_query_set_within_organisation():
            self.assertEqual(self.gp_organisation, user.userprofilebase.generalpracticeuser.organisation)

        # check if user is medidata they will get all user list
        amount_of_user_assume = 9
        amount_of_user_actual = len(self.medidata_user1.get_query_set_within_organisation())
        self.assertEqual(amount_of_user_assume, amount_of_user_actual)

    def test_get_user_role(self):

        # check client user
        self.assertEqual(self.claim_user_admin.get_my_role(), 'Client Admin')
        self.assertEqual(self.claim_user2.get_my_role(), 'Client User')

        # check medidata user
        self.assertEqual(self.medidata_user1.get_my_role(), 'Medidata User')

        # check gp user
        self.assertEqual(self.gp_user_admin.get_my_role(), 'General Practice Manager')
        self.assertEqual(self.gp_user2.get_my_role(), 'General Practice User')





