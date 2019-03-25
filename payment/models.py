from django.db import models
from organisations.models import OrganisationGeneralPractice, OrganisationClient
from common.models import TimeStampedModel

from decimal import Decimal

from typing import Union

class OrganisationFeeRate(models.Model):
    name = models.CharField(max_length=255)
    max_day_lvl_1 = models.PositiveSmallIntegerField(default=3, verbose_name='Top payment band until day')
    max_day_lvl_2 = models.PositiveSmallIntegerField(default=7, verbose_name='Medium payment band until day')
    max_day_lvl_3 = models.PositiveSmallIntegerField(default=11, verbose_name='Low payment band until day')
    max_day_lvl_4 = models.PositiveSmallIntegerField(default=12, verbose_name='Lowest payment band after day')
    amount_rate_lvl_1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for top payment band')
    amount_rate_lvl_2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for medium payment band')
    amount_rate_lvl_3 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for low payment band')
    amount_rate_lvl_4 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Earnings for lowest payment band')
    default = models.BooleanField(default=False)
    base = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'GP Organisation Fee Structure'
        verbose_name_plural = 'GP Organisation Fee Structures'
        ordering = ['amount_rate_lvl_1']

    def __str__(self):
        return "{band_name}: Top payment band is {top_payment}".format(band_name=self.name, top_payment=self.amount_rate_lvl_1)

    def get_fee_rate(self, period_day: int) -> Union[Decimal, int]:
        payment_band = [self.max_day_lvl_1, self.max_day_lvl_2, self.max_day_lvl_3, self.max_day_lvl_4]
        amount_rate = [self.amount_rate_lvl_1, self.amount_rate_lvl_2, self.amount_rate_lvl_3, self.amount_rate_lvl_4]
        for index, band in enumerate(payment_band):
            if period_day <= band:
                return amount_rate[index]
        return 0


class GpOrganisationFee(models.Model):
    gp_practice = models.OneToOneField(OrganisationGeneralPractice, on_delete=models.CASCADE, verbose_name='General Practice')
    organisation_fee = models.ForeignKey(OrganisationFeeRate, on_delete=models.CASCADE, verbose_name='Fee Rate')

    class Meta:
        verbose_name = 'GP Organisation Fee Relation'
        verbose_name_plural = 'GP Organisation Fee Relations'

    def __str__(self):
        return "{gp_name}-{organisation_fee_name}".format(gp_name=self.gp_practice.name, organisation_fee_name=self.organisation_fee.name)


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
    vat = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='VAT(%)', default=20)

    class Meta:
        verbose_name = 'Client Instruction Volume Fee structure'
        verbose_name_plural = 'Client Instruction Volume Fee structures'

    def __str__(self):
        return "Fee Structure: {}".format(self.client_organisation)

    def get_fee_rate(self, volume_amount: int) -> Union[Decimal, int]:
        volume_band = [self.max_volume_band_lowest, self.max_volume_band_low, self.max_volume_band_medium, self.max_volume_band_top]
        fee_rate = [self.fee_rate_lowest, self.fee_rate_low, self.fee_rate_medium, self.fee_rate_top]
        for index, band in enumerate(volume_band):
            if volume_amount <= band:
                return fee_rate[index]
        return 0
