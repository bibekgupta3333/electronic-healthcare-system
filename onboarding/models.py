from django.db import models
from organisations.models import OrganisationGeneralPractice
from common.models import TimeStampedModel


class EMRSetup(TimeStampedModel, models.Model):
    surgery_name = models.CharField(max_length=255)
    surgery_code = models.CharField(max_length=255)
    surgery_email = models.EmailField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    pm_name = models.CharField(max_length=255)
    pm_email = models.EmailField(max_length=255)
    receive_email = models.EmailField(max_length=255, null=True, blank=True)
    gp_name = models.CharField(max_length=255)
    primary_care = models.CharField(max_length=2, choices=OrganisationGeneralPractice.GP_OP_SYS_CHOICES)
    person_completeing = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    accept_policy = models.BooleanField(default=False)
    consented = models.BooleanField(default=False)
