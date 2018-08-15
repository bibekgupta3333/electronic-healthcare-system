from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class OrganizationBase(models.Model):
    trading_name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_name = models.CharField(max_length=255)
    contact_telephone = PhoneNumberField()
    contact_email = models.EmailField()
    generic_telephone = PhoneNumberField()
    generic_email = models.EmailField()
    fax_number = PhoneNumberField()
    companies_house_number = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=255)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    deleted_timestamp = models.DateTimeField(editable=False, null=True)

    class Meta:
        verbose_name = 'Organization'

    def __str__(self):
        return self.trading_name


class OrganizationClient(OrganizationBase):
    INSURANCE_UNDERWRITER = 1
    INSURANCE_CLAIM = 2
    MEDIDATA = 3
    MEDICOLEGAL = 4

    ROLE_CHOICES = (
        (INSURANCE_UNDERWRITER, 'Insurance Underwriter'),
        (INSURANCE_CLAIM, 'Insurance Claim'),
        (MEDIDATA, 'MediData'),
        (MEDICOLEGAL, 'Medicolegal')
    )

    type = models.IntegerField(choices=ROLE_CHOICES)
    fca_number = models.CharField(max_length=255, blank=True)
    division = models.TextField(blank=True)
    can_create_amra = models.BooleanField(default=False)
    can_create_sars = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Organization Client'

    def __str__(self):
        return self.trading_name


class OrganizationGeneralPractice(OrganizationBase):
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

    class Meta:
        verbose_name = 'Organization GeneralPractice'

    def __str__(self):
        return self.trading_name

