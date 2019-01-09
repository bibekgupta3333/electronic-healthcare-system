from django.test import TestCase
from accounts.models import User, GENERAL_PRACTICE_USER


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
