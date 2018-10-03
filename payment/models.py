from django.db import models
from organisations.models import OrganisationGeneralPractice
from common.models import TimeStampedModel


class OrganisationFee(TimeStampedModel, models.Model):
    gp_practice = models.OneToOneField(OrganisationGeneralPractice, on_delete=models.CASCADE, verbose_name='General Practice')
    max_day_lvl_1 = models.PositiveSmallIntegerField()
    max_day_lvl_2 = models.PositiveSmallIntegerField()
    max_day_lvl_3 = models.PositiveSmallIntegerField()
    amount_rate_lvl_1 = models.DecimalField(max_digits=5, decimal_places=2)
    amount_rate_lvl_2 = models.DecimalField(max_digits=5, decimal_places=2)
    amount_rate_lvl_3 = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'Organisation Fee Structure'
        verbose_name_plural = 'Organisation Fee Structures'

    def __str__(self):
        return "Fee Structure: {}".format(self.gp_practice)