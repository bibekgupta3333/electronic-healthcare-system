from django.db import models
from organisations.models import OrganisationGeneralPractice, OrganisationClient
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
        verbose_name = 'GP Organisation Fee Structure'
        verbose_name_plural = 'GP Organisation Fee Structures'

    def __str__(self):
        return "Fee Structure: {}".format(self.gp_practice)


class InstructionVolumeFee(models.Model):
    client_organisation = models.OneToOneField(OrganisationClient, on_delete=models.CASCADE, verbose_name='Client Organisation')
    max_volume_band_lowest = models.PositiveIntegerField(verbose_name='Max volume of Lowest band')
    max_volume_band_low = models.PositiveIntegerField(verbose_name='Max volume of Low band')
    max_volume_band_medium = models.PositiveIntegerField(verbose_name='Max volume of Medium band')
    max_volume_band_top = models.PositiveIntegerField(verbose_name='Max volume of Top band')
    fee_rate_lowest = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for Lowest band(£)')
    fee_rate_low = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for Low band(£)')
    fee_rate_medium = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for Medium band(£)')
    fee_rate_top = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for Top band(£)')

    class Meta:
        verbose_name = 'Client Organisation Fee structure'
        verbose_name_plural = 'Client Organisation Fee structures'

    def __str__(self):
        return "Fee Structure: {}".format(self.client_organisation)

