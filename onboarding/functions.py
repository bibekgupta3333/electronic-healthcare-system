from accounts.models import User, GeneralPracticeUser
from accounts.models import GENERAL_PRACTICE_USER
from organisations.models import OrganisationGeneralPractice
from payment.models import OrganisationFee
from .forms import BankDetailsEmrSetUpStage2Form
from .models import EMRSetup


def create_gp_user(gp_organisation: OrganisationGeneralPractice, user_form: dict=None, emr_setup: EMRSetup=None) -> dict:
    password = User.objects.make_random_password()
    if user_form:
        if not User.objects.filter(email=user_form['email']).exists():
            user = User.objects._create_user(
                email=user_form['email'],
                username="{}.{}".format(user_form['first_name'],user_form['last_name']),
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
    elif emr_setup:
        if not User.objects.filter(email=emr_setup.pm_email).exists():
            gp_manager_user = User.objects._create_user(
                email=emr_setup.pm_email,
                username=emr_setup.pm_name,
                password=password,
                first_name=emr_setup.pm_name,
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


def create_gp_organisation(emr_setup: EMRSetup, bank_details_form: BankDetailsEmrSetUpStage2Form) -> OrganisationGeneralPractice:
    gp_address = ' '.join([
        emr_setup.address_line1,
        emr_setup.address_line2,
        emr_setup.city,
        emr_setup.post_code
    ])

    gp_organisation = OrganisationGeneralPractice.objects.create(
        trading_name=emr_setup.surgery_name,
        legal_name=emr_setup.surgery_name,
        address=gp_address,
        contact_telephone=emr_setup.phone,
        contact_email=emr_setup.receive_email,
        generic_telephone=emr_setup.phone,
        generic_email=emr_setup.surgery_email,
        operating_system=emr_setup.primary_care,
        practice_code=emr_setup.surgery_code,
        payment_bank_holder_name=bank_details_form.cleaned_data['bank_account_name'],
        payment_bank_sort_code=bank_details_form.cleaned_data['bank_account_sort_code'],
        payment_bank_account_number=bank_details_form.cleaned_data['bank_account_number'],
    )

    return gp_organisation


def create_gp_payments_fee(bank_details_form: BankDetailsEmrSetUpStage2Form, gp_organisation: OrganisationGeneralPractice) -> OrganisationFee:
    organisation_fee = OrganisationFee.objects.create(
        gp_practice=gp_organisation,
        max_day_lvl_1=3,
        max_day_lvl_2=6,
        max_day_lvl_3=10,
        max_day_lvl_4=11,
        amount_rate_lvl_1=bank_details_form.cleaned_data['received_within_3_days'],
        amount_rate_lvl_2=bank_details_form.cleaned_data['received_within_4_to_6_days'],
        amount_rate_lvl_3=bank_details_form.cleaned_data['received_within_7_to_10_days'],
        amount_rate_lvl_4=bank_details_form.cleaned_data['received_after_10_days'],
    )

    return organisation_fee
