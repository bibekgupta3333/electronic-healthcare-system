from accounts.models import User, GeneralPracticeUser
from accounts.models import GENERAL_PRACTICE_USER
from organisations.models import OrganisationGeneralPractice
from payment.models import OrganisationFee
from .forms import BankDetailsEmrSetUpStage2Form
from accounts.models import PracticePreferences
import random
import string


def create_gp_user(gp_organisation: OrganisationGeneralPractice, user_form: dict=None) -> dict:
    password = User.objects.make_random_password()
    if user_form:
        if not User.objects.filter(email=user_form['email']).exists():
            user = User.objects._create_user(
                email=user_form['email'],
                username=''.join(random.choices(string.ascii_letters, k=10)),
                password=password,
                first_name=user_form['first_name'],
                last_name=user_form['last_name'],
                type=GENERAL_PRACTICE_USER,
            )

            general_pratice_user = GeneralPracticeUser.objects.create(
                user=user,
                title=user_form['title'],
                role=user_form['role'],
                organisation=gp_organisation,
                code=user_form['gp_code'],
            )
            return {
                'general_pratice_user': general_pratice_user,
                'password': password
            }
    elif gp_organisation:
        if not User.objects.filter(email=gp_organisation.practicemanager_email).exists():
            gp_manager_first_name = gp_organisation.practicemanagername_c.split(' ')[0]
            gp_manager_last_name = gp_organisation.practicemanagername_c.split(' ')[1]
            gp_manager_user = User.objects._create_user(
                email=gp_organisation.practicemanager_email,
                username=''.join(random.choices(string.ascii_letters, k=10)),
                password=password,
                first_name=gp_manager_first_name,
                last_name=gp_manager_last_name,
                type=GENERAL_PRACTICE_USER,
                is_staff=True,
            )

            general_pratice_user = GeneralPracticeUser.objects.create(
                user=gp_manager_user,
                role=GeneralPracticeUser.PRACTICE_MANAGER,
                organisation=gp_organisation,
            )

            return {
                'general_pratice_user': general_pratice_user,
                'password': password
            }
    else:
        return {}


def create_gp_payments_fee(bank_details_form: BankDetailsEmrSetUpStage2Form, gp_organisation: OrganisationGeneralPractice) -> OrganisationFee:
    organisation_fee = OrganisationFee.objects.update_or_create(
        gp_practice=gp_organisation,
        defaults={
            'max_day_lvl_1': 3,
            'max_day_lvl_2': 6,
            'max_day_lvl_3': 10,
            'max_day_lvl_4': 11,
            'amount_rate_lvl_1': bank_details_form.cleaned_data['received_within_3_days'],
            'amount_rate_lvl_2': bank_details_form.cleaned_data['received_within_4_to_6_days'],
            'amount_rate_lvl_3': bank_details_form.cleaned_data['received_within_7_to_10_days'],
            'amount_rate_lvl_4': bank_details_form.cleaned_data['received_after_10_days'],
        }
    )

    return organisation_fee[0]
