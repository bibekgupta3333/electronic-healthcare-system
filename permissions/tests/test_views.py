from django.test import TestCase
from model_mommy import mommy
from accounts.models import User, GENERAL_PRACTICE_USER, GeneralPracticeUser
from django.contrib.auth.models import Permission


class PermissionTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(User, type=GENERAL_PRACTICE_USER)
        mommy.make(GeneralPracticeUser, user=self.user)
        self.client.force_login(self.user, backend=None)


class UserManagementWithoutPermissionTest(PermissionTestCase):
    def test_view_user_management(self):
        response = self.client.get('/accounts/view-users/')
        self.assertEqual(302, response.status_code)

    def test_add_user_management(self):
        response = self.client.get('/accounts/create-user/')
        self.assertEqual(302, response.status_code)

    def test_update_permission(self):
        response = self.client.get('/accounts/update-permission/')
        self.assertEqual(302, response.status_code)


class UserManagementTest(PermissionTestCase):
    def test_view_user_management(self):
        permission = Permission.objects.get(codename='view_user_management')
        self.user.user_permissions.add(permission)
        response = self.client.get('/accounts/view-users/')
        self.assertEqual(200, response.status_code)

    def test_add_user_management(self):
        permission = Permission.objects.get(codename='add_user_management')
        self.user.user_permissions.add(permission)
        response = self.client.get('/accounts/create-user/')
        self.assertEqual(200, response.status_code)

    def test_update_permission(self):
        permission = Permission.objects.get(codename='change_instructionpermission')
        self.user.user_permissions.add(permission)
        response = self.client.get('/accounts/update-permission/')
        self.assertEqual(response.url, '/accounts/view-users/?show=True')
