from django.db import models
from common.models import TimeStampedModel


class OrganisationBase(models.Model):
    trading_name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255)
    address = models.TextField(max_length=255)

    class Meta:
        verbose_name = 'Organisation'
        permissions = (
            ('view_user_management', 'Can view User Management'),
            ('add_user_management', 'Can add User Management'),
            ('change_user_management', 'Can change User Management'),
            ('delete_user_management', 'Can delete User Management')
        )

    def __str__(self):
        return self.trading_name


class OrganisationMedidata(OrganisationBase):
    class Meta:
        verbose_name = 'Organisation Medidata'

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
    contact_name = models.CharField(max_length=255, blank=True)
    contact_telephone = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    generic_telephone = models.CharField(max_length=255, blank=True)
    generic_email = models.EmailField(blank=True)
    fax_number = models.CharField(max_length=255, blank=True)
    companies_house_number = models.CharField(max_length=255, blank=True)
    vat_number = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Organisation Client'

    def __str__(self):
        return self.trading_name


class OrganisationGeneralPractice(models.Model):
    GP_OP_SYS_CHOICES = (
        ('EMISWeb', 'EMIS-Web'),
        ('HealthyV5', 'Healthy V5'),
        ('LV', 'EMIS-LV'),
        ('PCS', 'PCS'),
        ('Practice Manager', 'Practice Manager'),
        ('PREMIERE', 'Premiere'),
        ('SYNERGY', 'Synergy'),
        ('SystmOne', 'SystmOne'),
        ('Vision 3', 'Vision 3'),
        ('VA', 'Vision Anywhere'),
        ('MT', 'Microtest'),
        ('OT', 'Other')
    )

    PAYMENT_TIMING_CHOICES = (
        ('AR', 'Arrears'),
        ('AD', 'Advance')
    )
    region = models.CharField(max_length=255, blank=True)
    comm_area = models.CharField(max_length=255, blank=True)
    practcode = models.CharField(max_length=255, primary_key=True, unique=True)
    name = models.CharField(max_length=255, blank=True)
    billing_address_street = models.CharField(max_length=255, blank=True)
    billing_address_city = models.CharField(max_length=22, blank=True)
    billing_address_state = models.CharField(max_length=16, blank=True)
    billing_address_postalcode = models.CharField(max_length=8, blank=True)
    phone_office = models.CharField(max_length=28, blank=True)
    phone_alternate = models.CharField(max_length=20, blank=True)
    organisation_email = models.CharField(max_length=255, blank=True)
    practicemanagername_c = models.CharField(max_length=34, blank=True)
    practicemanager_job_title = models.CharField(max_length=47, blank=True)
    practicemanager_email = models.CharField(max_length=54, blank=True)
    practicemanager_phone = models.CharField(max_length=28, blank=True)
    patientlistsize_c = models.CharField(max_length=255, blank=True)
    sitenumber_c = models.CharField(max_length=255, blank=True)
    employees = models.CharField(max_length=2, blank=True)
    ownership = models.CharField(max_length=45, blank=True)
    ccg_health_board_c = models.CharField(max_length=47, blank=True)
    fax = models.CharField(max_length=47, blank=True)
    gp_operating_system = models.CharField(max_length=32, choices=GP_OP_SYS_CHOICES, blank=True)
    website = models.CharField(max_length=255, blank=True)

    operating_system_socket_endpoint = models.CharField(max_length=255, blank=True)
    operating_system_auth_token = models.CharField(max_length=255, blank=True)
    payment_timing = models.CharField(max_length=2, choices=PAYMENT_TIMING_CHOICES, blank=True)
    payment_bank_holder_name = models.CharField(max_length=255, blank=True)
    payment_bank_sort_code = models.CharField(max_length=255, blank=True)
    payment_bank_account_number = models.CharField(max_length=255, blank=True)
    payment_preference = models.CharField(max_length=255, blank=True)

    accept_policy = models.BooleanField(default=False)
    live = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Organisation GeneralPractice'

    def __str__(self):
        return self.name
