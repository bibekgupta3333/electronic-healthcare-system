from django.db import models
from fernet_fields import EncryptedCharField


# Create your models here.
class EmisAPIConfig(models.Model):
    emis_organisation_id = models.CharField(max_length=255)
    emis_username = models.CharField(max_length=255)
    emis_password = EncryptedCharField(max_length=255)

    def __str__(self):
        return "{} - {}".format(self.emis_organisation_id, self.emis_username)
