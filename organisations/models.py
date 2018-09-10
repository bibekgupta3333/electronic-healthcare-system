from django.db import models
from common.models import TimeStampedModel


class OrganisationMedidata(models.Model):
    trading_name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255)
    address = models.TextField(max_length=255)

    class Meta:
        verbose_name = 'Organisation Medidata'

    def __str__(self):
        return self.trading_name


class OrganisationBase(OrganisationMedidata):
    contact_name = models.CharField(max_length=255, blank=True)
    contact_telephone = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    generic_telephone = models.CharField(max_length=255, blank=True)
    generic_email = models.EmailField(blank=True)
    fax_number = models.CharField(max_length=255, blank=True)
    companies_house_number = models.CharField(max_length=255, blank=True)
    vat_number = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Organisation'

    def __str__(self):
        return self.trading_name


class OrganisationClient(OrganisationBase):
    INSURANCE_UNDERWRITER = 1
    INSURANCE_CLAIM = 2
    MEDICOLEGAL = 3

    ROLE_CHOICES = (
        (INSURANCE_UNDERWRITER, 'Insurance Underwriter'),
        (INSURANCE_CLAIM, 'Insurance Claim'),
        (MEDICOLEGAL, 'Medicolegal')
    )

    type = models.IntegerField(choices=ROLE_CHOICES)
    fca_number = models.CharField(max_length=255, blank=True)
    division = models.TextField(blank=True)
    can_create_amra = models.BooleanField(default=False)
    can_create_sars = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Organisation Client'

    def __str__(self):
        return self.trading_name


class OrganisationGeneralPractice(OrganisationBase):
    GP_OP_SYS_CHOICES = (
        ('EW', 'EMIS-Web'),
        ('EP', 'EMIS-PCS'),
        ('EL', 'EMIS-LV'),
        ('ST', 'Systml'),
        ('VT', 'Vision Three'),
        ('VA', 'Vision Anywhere'),
        ('MT', 'Microtest'),
        ('OT', 'Other')
    )

    PAYMENT_TIMING_CHOICES = (
        ('AR', 'Arrears'),
        ('AD', 'Advance')
    )

    operating_system = models.CharField(max_length=2, choices=GP_OP_SYS_CHOICES)
    operating_system_socket_endpoint = models.CharField(max_length=255)
    operating_system_auth_token = models.CharField(max_length=255)
    practice_code = models.CharField(max_length=255)
    payment_timing = models.CharField(max_length=2, choices=PAYMENT_TIMING_CHOICES)
    payment_bank_holder_name = models.CharField(max_length=255)
    payment_bank_sort_code = models.CharField(max_length=255)
    payment_bank_account_number = models.CharField(max_length=255)
    payment_preference = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Organisation GeneralPractice'

    def __str__(self):
        return self.trading_name


class NHSgpPractice(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    reference = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255)
    address_line3 = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'NHS GP Practice'

    def __str__(self):
        return self.name