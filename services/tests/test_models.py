from django.test import TestCase

from model_mommy import mommy

from services.models import EmisAPIConfig


class EmisAPIConfigTest(TestCase):
    def test_string_representation(self):
        emis_api_config = mommy.make(
            EmisAPIConfig, emis_organisation_id='12345',
            emis_username='emis_user', emis_password='password'
        )
        self.assertEqual(str(emis_api_config), '12345 - emis_user')
