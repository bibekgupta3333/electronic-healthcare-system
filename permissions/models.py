from django.db import models
from accounts.models import GeneralPracticeUser
from common.models import TimeStampedModel


class InstructionPermission(TimeStampedModel, models.Model):
    role = models.IntegerField(choices=GeneralPracticeUser.ROLE_CHOICES, verbose_name='Role')
    create_sars = models.BooleanField(default=False, verbose_name="Create SARS")
    reject_amra = models.BooleanField(default=False, verbose_name="Reject AMRA")
    reject_sars = models.BooleanField(default=False, verbose_name="Reject SARS")
    process_amra = models.BooleanField(default=False, verbose_name="Process AMRA")
    process_sars = models.BooleanField(default=False, verbose_name="Process SARS")
    allocate_gp = models.BooleanField(default=False, verbose_name="Allocate to other user to process")
    sign_off_amra = models.BooleanField(default=False, verbose_name="Sign off AMRA")
    sign_off_sars = models.BooleanField(default=False, verbose_name="Sign off SARS")
    view_completed_amra = models.BooleanField(default=False, verbose_name="View completed AMRA")
    view_completed_sars = models.BooleanField(default=False, verbose_name="View completed SARS")

    class Meta:
        unique_together = ["role"]

    def __str__(self):
        return self.get_role_display()
