from django.db import models
from organisations.models import OrganisationGeneralPractice
from common.models import TimeStampedModel


class OrganisationFee(models.Model):
    gp_practice = models.OneToOneField(OrganisationGeneralPractice, on_delete=models.CASCADE, verbose_name='General Practice')
    max_day_lvl_1 = models.PositiveSmallIntegerField(verbose_name='Top payment band until day')
    max_day_lvl_2 = models.PositiveSmallIntegerField(verbose_name='Medium payment band until day')
    max_day_lvl_3 = models.PositiveSmallIntegerField(verbose_name='Low payment band until day')
    max_day_lvl_4 = models.PositiveSmallIntegerField(verbose_name='Lowest payment band after day')
    amount_rate_lvl_1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for top payment band')
    amount_rate_lvl_2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for medium payment band')
    amount_rate_lvl_3 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for low payment band')
    amount_rate_lvl_4 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for lowest payment band')

    class Meta:
        verbose_name = 'Organisation Fee Structure'
        verbose_name_plural = 'Organisation Fee Structures'

    def __str__(self):
        return "Fee Structure: {}".format(self.gp_practice)
