from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import gettext_lazy as _

from organisations.models import OrganisationGeneralPractice, OrganisationClient, OrganisationMedidata
from common.models import TimeStampedModel

SEX_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)

TITLE_CHOICE = (
    ('', '----'),
    ('DR', 'Dr.'),
    ('MR', 'Mr.'),
    ('MRS', 'Mrs.'),
    ('MS', 'Ms.'),
    ('MX', 'Mx.')
)

MEDIDATA_USER = 'MEDI'
CLIENT_USER = 'CLT'
GENERAL_PRACTICE_USER = 'GP'
PATIENT_USER = 'PAT'

USER_TYPE_CHOICES = (
    (MEDIDATA_USER, 'Medidata'),
    (CLIENT_USER, 'Client'),
    (GENERAL_PRACTICE_USER, 'General Practice'),
    (PATIENT_USER, 'Patient')
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
        verbose_name='email',
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
            elif hasattr(self.userprofilebase, 'medidatauser'):
                return User.objects.filter(type__in=[MEDIDATA_USER, CLIENT_USER, GENERAL_PRACTICE_USER])
            else:
                return User.objects.all()
        else:
            return None

    def get_short_my_role(self):
        profile = self.userprofilebase
        if self.type == MEDIDATA_USER:
            return 'Medidata'
        elif self.type == CLIENT_USER and hasattr(profile, 'clientuser'):
            return profile.clientuser.get_role_display() or '--'
        elif self.type == GENERAL_PRACTICE_USER and hasattr(profile, 'generalpracticeuser'):
            return profile.generalpracticeuser.get_role_display() or '--'
        else:
            return 'Patient'

    def get_my_role(self):
        profile = self.userprofilebase
        if self.type == MEDIDATA_USER:
            return 'Medidata User'
        elif self.type == CLIENT_USER and hasattr(profile, 'clientuser'):
            role = profile.clientuser.role
            if role == ClientUser.CLIENT_ADMIN:
                return 'Client Admin'
            else:
                return 'Client User'
        elif self.type == GENERAL_PRACTICE_USER and hasattr(profile, 'generalpracticeuser'):
            role = profile.generalpracticeuser.role
            if role == GeneralPracticeUser.PRACTICE_MANAGER:
                return 'General Practice Manager'
            elif role == GeneralPracticeUser.GENERAL_PRACTICE:
                return 'General Practice User'
            else:
                return 'SARS'
        else:
            return 'Patient User'


class UserProfileBase(TimeStampedModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=3, choices=TITLE_CHOICE, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    maiden_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address_name_number = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    address_line3 = models.CharField(max_length=255, blank=True)
    address_line4 = models.CharField(max_length=255, blank=True)
    address_postcode = models.CharField(max_length=255, blank=True)
    address_country = models.CharField(max_length=255, blank=True)
    telephone_home = models.CharField(max_length=255, blank=True)
    telephone_mobile = models.CharField(max_length=255, blank=True)
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
    CLIENT_ADMIN = 0
    CLIENT_USER = 1

    ROLE_CHOICES = (
        (CLIENT_ADMIN, 'Client Admin'),
        (CLIENT_USER, 'Client')
    )

    role = models.IntegerField(choices=ROLE_CHOICES, null=True, blank=True, verbose_name='Role')
    organisation = models.ForeignKey(OrganisationClient, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Client User'

    def __str__(self):
        return self.user.first_name


class GeneralPracticeUser(UserProfileBase):
    PRACTICE_MANAGER = 0
    GENERAL_PRACTICE = 1
    SARS_RESPONDER = 2

    ROLE_CHOICES = (
        ('', '----'),
        (PRACTICE_MANAGER, 'Manager'),
        (GENERAL_PRACTICE, 'GP'),
        (SARS_RESPONDER, 'SARS')
    )

    role = models.IntegerField(choices=ROLE_CHOICES, null=True, blank=True, verbose_name='Role')
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
        return self.user.first_name


class Patient(UserProfileBase):
    organisation_gp = models.ForeignKey(OrganisationGeneralPractice, on_delete=models.CASCADE)
    nhs_number = models.CharField(max_length=10, blank=True)
    emis_number = models.CharField(max_length=255)
    vision_number = models.CharField(max_length=255)
    systmone_number = models.CharField(max_length=255)
    microtest_number = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Patient User'

    def __str__(self):
        return self.user.first_name
