from django.db import models
from accounts.models import GeneralPracticeUser
from common.models import TimeStampedModel
from organisations.models import OrganisationGeneralPractice


class InstructionPermission(models.Model):
    role = models.IntegerField(choices=GeneralPracticeUser.ROLE_CHOICES, verbose_name='Role')
    organisation = models.ForeignKey(OrganisationGeneralPractice, on_delete=models.CASCADE, null=True)
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
        unique_together = ["role", "organisation"]

    def __str__(self):
        return '%s : %s'%(self.get_role_display(),self.organisation.__str__())
