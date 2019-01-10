from django.test import RequestFactory, TestCase
from django.test import tag, Client
from django.utils import timezone
from django.shortcuts import render
from django_tables2 import RequestConfig

from model_mommy import mommy

from organisations.models import OrganisationGeneralPractice
from accounts.models import ClientUser, GeneralPracticeUser, User, GENERAL_PRACTICE_USER, UserProfileBase

import datetime

class TestViews( TestCase ):
    def setUp( self ):
        #   Prepare request for test.
        self.userNameTest = 'testMedi007'
        self.method = 'POST'
        self.request = RequestFactory()

        #   create User_A in DB.
        #   create userProfile.
        self.userName_A = 'pringleUser'
        self.firstName_A = 'Pringle'
        self.lastName_A = 'Iphone'
        self.email_A = 'medi001@mohara.co'
        self.password_A = 'secret'
        self.role_A = '1'

        #   create organisationProfile
        self.organisation_A = 'Test organisation.'
        self.practCode_A = 'TEST0001'

        self.gp_practice = mommy.make( OrganisationGeneralPractice, name = self.organisation_A, practcode = self.practCode_A )
        self.userProfileA = mommy.make( User, username = self.userName_A, password = self.password_A, first_name = self.firstName_A, last_name = self.lastName_A, email = self.email_A )
        self.userA = mommy.make( GeneralPracticeUser,
            organisation = self.gp_practice,
            user = self.userProfileA,
            role = self.role_A,
            title = 'DR'
        )
        
        #   create userTest for request
        user = User.objects.create( username='testuser', email = 'testuser@mohara.co', first_name='testuser', is_active = True, type = GENERAL_PRACTICE_USER )
        user.set_password('secret')
        user.save()

        self.request_user = mommy.make(
            GeneralPracticeUser,
            organisation = self.gp_practice,
            user = user,
            role = 0,
            title = 'MR'
        )


    def test_create_user_exist( self ):
        #   Test create function but fail. Because exist account
        firstName = 'Jirayu'
        lastName = 'Oopipat'
        email = self.email_A
        password = 'secret1'
        role = '1'

        self.client.login( email = 'testuser@mohara.co', password = 'secret' )
        response = self.client.post('/accounts/create-user/', {
            'user_role' : role,
            'first_name': firstName,
            'last_name': lastName,
            'email': email,
            'password' : password
        })

        expectedMassage = 'User Account Existing In Database'
        messages = list( response.context[ 'messages' ] )

        self.assertEqual( 200, response.status_code )
        self.assertEqual( 1, len( messages ) )
        self.assertEqual( expectedMassage, str( messages[0] ) )

    def test_create_user_success( self ):
        #   Test create user and success.
        firstName = 'Jirayu'
        lastName = 'Oopipat'
        email = 'snoopy@mohara.co'
        password = 'secret2'
        role = '1'

        self.client.login( email = 'testuser@mohara.co', password = 'secret' )
        response = self.client.post('/accounts/create-user/', {
            'user_role' : role,
            'first_name': firstName,
            'last_name': lastName,
            'email': email,
            'password' : password
        })

        queryResultUser = User.objects.all()
        resultUser = queryResultUser[2]

        self.assertEqual( 302, response.status_code )
        self.assertEqual( 3, len( queryResultUser ) )
        self.assertEqual( email, resultUser.email )
        self.assertEqual( email, resultUser.username )
        self.assertEqual( firstName, resultUser.first_name )
        self.assertEqual( lastName, resultUser.last_name )
        self.assertEqual( 'General Practice User', resultUser.get_my_role() )

    def test_create_user_fail( self ):
        #   Test create user but fail. Because invalid form.
        firstName = 'Jirayu'
        lastName = 'Oopipat'

        self.client.login( email = 'testuser@mohara.co', password = 'secret' )
        response = self.client.post('/accounts/create-user/', {
            'first_name': firstName,
            'last_name': lastName,
        })

        expectedMassage = 'Please input all the fields properly.'
        messages = list( response.context[ 'messages' ] )

        self.assertEqual( 200, response.status_code )
        self.assertEqual( 1, len( messages ) )
        self.assertEqual( expectedMassage, str( messages[0] ) )

class LoginTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(
            email='user@gmail.com',
            type=GENERAL_PRACTICE_USER
        )
        user.set_password('User1234')
        user.save()

    def test_login_view(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(200, response.status_code)

    def test_two_factor_missing_data_redirect(self):
        response = self.client.get('/accounts/two-factor/')
        self.assertEqual(302, response.status_code)
        self.assertEqual("/accounts/login/", response.url)

    def test_login_ip_with_n3_hscn_redirect(self):
        response = self.client.post('/accounts/login/', {'username': 'user@gmail.com', 'password': 'User1234'}, REMOTE_ADDR="172.17.5.3")
        self.assertEqual(302, response.status_code)
        self.assertEqual("/instruction/view-pipeline/", response.url)

    def test_login_ip_outside_n3_hscn_redirect(self):
        response = self.client.post('/accounts/login/', {'username': 'user@gmail.com', 'password': 'User1234'}, REMOTE_ADDR="127.0.0.1")
        self.assertEqual(302, response.status_code)
        self.assertEqual("/accounts/two-factor/", response.url)
