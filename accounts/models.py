from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from organisations.models import OrganisationGeneralPractice, OrganisationClient, OrganisationMedidata

from phonenumber_field.modelfields import PhoneNumberField

SEX_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)

MEDIDATA_USER = 'MEDI'
CLIENT_USER = 'CLT'
GENERAL_PRACTICE_USER = 'GP'

USER_TYPE_CHOICES = (
    (MEDIDATA_USER, 'Medidata'),
    (CLIENT_USER, 'Client'),
    (GENERAL_PRACTICE_USER, 'General Practice')
)


class MyUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    type = models.CharField(max_length=4, choices=USER_TYPE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = MyUserManager()

    def get_query_set_within_organisation(self, organisation=None):
        if self.userprofilebase:
            if hasattr(self.userprofilebase, 'generalpracticeuser'):
                organisation = self.userprofilebase.generalpracticeuser.organisation
                return User.objects.filter(userprofilebase__generalpracticeuser__organisation=organisation)
            elif hasattr(self.userprofilebase, 'clientuser'):
                organisation = self.userprofilebase.clientuser.organisation
                return User.objects.filter(userprofilebase__clientuser__organisation=organisation)
            else:
                return None


class UserProfileBase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    maiden_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address_name_number = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    address_line3 = models.CharField(max_length=255, blank=True)
    address_line4 = models.CharField(max_length=255, blank=True)
    address_postcode = models.CharField(max_length=255, blank=True)
    address_country = models.CharField(max_length=255, blank=True)
    telephone_home = PhoneNumberField(blank=True)
    telephone_mobile = PhoneNumberField(blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)

    class Meta:
        verbose_name = 'User Profile Base'
        verbose_name_plural = 'User Profile Bases'

    def __str__(self):
        return self.user.email + "User Profile"


class MedidataUser(UserProfileBase):
    organisation = models.ForeignKey(OrganisationMedidata, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Medidata User'

    def __str__(self):
        return 'Medidata' + self.user.first_name


class ClientUser(UserProfileBase):
    organisation = models.ForeignKey(OrganisationClient, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Client User'

    def __str__(self):
        return 'Client: ' + self.user.first_name


class GeneralPracticeUser(UserProfileBase):
    organisation = models.ForeignKey(OrganisationGeneralPractice, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, blank=True)
    payment_bank_holder_name = models.CharField(max_length=255, blank=True)
    payment_bank_account_number = models.CharField(max_length=255, blank=True)
    payment_bank_sort_code = models.CharField(max_length=255, blank=True)
    can_complete_amra = models.BooleanField(default=False)
    can_complete_sars = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'General Practice User'

    def __str__(self):
        return 'GP: ' + self.user.first_name
