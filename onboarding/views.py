from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings
from django.forms import formset_factory
from django.http import JsonResponse
from django.contrib import messages
from .functions import *
from .forms import *
from accounts.models import GpPractices
from accounts.forms import PMForm
from services.emisapiservices.services import GetEmisStatusCode
from organisations.models import OrganisationGeneralPractice
from permissions.functions import generate_gp_permission
import random
import string


def sign_up(request):
    surgery_form = SurgeryForm()
    pm_form = PMForm()

    if request.method == "POST":
        surgery_form = SurgeryForm(request.POST)
        pm_form = PMForm(request.POST)
        selected_surgery_name = request.POST.get('surgery_name', '')
        selected_practice_code = request.POST.get('practice_code', '')
        selected_post_code = request.POST.get('postcode', '')

        if surgery_form.is_valid() and pm_form.is_valid():
            gp_organisation = surgery_form.save()
            pm_form.save__with_gp(gp_organisation=gp_organisation)
            if not surgery_form.cleaned_data.get('operating_system') == 'EMISWeb':
                message_1 = 'Thank you for completing part one of the eMR registration process. It’s great to have you on board.'
                message_2 = 'We will be in touch with you shortly to complete the set up process so that you can process SARs in seconds.'
                message_3 = 'We look forward to working with you in the very near future. eMR Support Team'
                return render(request, 'onboarding/emr_message.html', context={
                    'message_1': message_1,
                    'message_2': message_2,
                    'message_3': message_3
                })
            if gp_organisation.practcode[:4] == 'TEST':
                gp_organisation.operating_system_username = 'michaeljtbrooks'
                gp_organisation.operating_system_salt_and_encrypted_password = 'Medidata2018'
            else:
                initial_password = random.choices(string.ascii_uppercase, k=1)
                body_password = random.choices(string.ascii_letters+string.digits, k=12)
                tail_password = random.choices(string.digits, k=1)
                password = ''.join(initial_password + body_password + tail_password)
                gp_organisation.operating_system_salt_and_encrypted_password = password
                gp_organisation.operating_system_username = 'medidata_access'
            gp_organisation.save()
            generate_gp_permission(gp_organisation)
            return redirect('onboarding:emis_setup', practice_code=gp_organisation.practcode)

        return render(request, 'onboarding/sign_up.html', {
            'selected_surgery_name': selected_surgery_name,
            'selected_practice_code': selected_practice_code,
            'selected_post_code': selected_post_code,
            'surgery_form': surgery_form,
            'pm_form': pm_form,
            'GET_ADDRESS_API_KEY': settings.GET_ADDRESS_API_KEY
        })

    return render(request, 'onboarding/sign_up.html', {
        'surgery_form': surgery_form,
        'pm_form': pm_form,
        'GET_ADDRESS_API_KEY': settings.GET_ADDRESS_API_KEY
    })


def emis_setup(request, practice_code):
    header_title = "Sign up: eMR with EMISweb"
    gp_organisation = OrganisationGeneralPractice.objects.filter(practcode=practice_code).first()

    if request.method == "POST":
        surgery_update_form = SurgeryUpdateForm(request.POST)
        if surgery_update_form.is_valid():
            gp_organisation.operating_system_organisation_code = surgery_update_form.cleaned_data['emis_org_code']
            gp_organisation.gp_operating_system = surgery_update_form.cleaned_data['operating_system']
            gp_organisation.save()

    surgery_update_form = SurgeryUpdateForm(initial={
        'surgery_name': gp_organisation.name,
        'surgery_code': gp_organisation.practcode,
        'emis_org_code': gp_organisation.operating_system_organisation_code,
        'operating_system': gp_organisation.gp_operating_system
    })

    return render(request, 'onboarding/emis_setup.html', {
        'header_title': header_title,
        'organisation_code': gp_organisation.operating_system_organisation_code,
        'practice_code': gp_organisation.practcode,
        'practice_password': gp_organisation.operating_system_salt_and_encrypted_password,
        'surgery_update_form': surgery_update_form
    })


def emr_setup_stage_2(request, practice_code=None):
    gp_organisation = get_object_or_404(OrganisationGeneralPractice, pk=practice_code)
    address = ' '.join([
        gp_organisation.billing_address_street,
        gp_organisation.billing_address_line_2,
        gp_organisation.billing_address_line_3,
        gp_organisation.billing_address_city,
        gp_organisation.billing_address_state
    ])

    surgery_form = SurgeryEmrSetUpStage2Form(initial={
        'surgery_name': gp_organisation.name,
        'surgery_code': gp_organisation.practcode,
        'address': address,
        'postcode': gp_organisation.billing_address_postalcode,
        'surgery_tel_number': gp_organisation.phone_office,
        'surgery_email': gp_organisation.organisation_email
    })

    UserEmrSetUpStage2Formset = formset_factory(UserEmrSetUpStage2Form, min_num=2, validate_min=True, extra=2)
    user_formset = UserEmrSetUpStage2Formset()
    bank_details_form = BankDetailsEmrSetUpStage2Form()
    surgery_email_form = SurgeryEmailForm(instance=gp_organisation)

    if request.method == "POST":
        user_formset = UserEmrSetUpStage2Formset(request.POST)
        bank_details_form = BankDetailsEmrSetUpStage2Form(request.POST)
        surgery_email_form = SurgeryEmailForm(request.POST, instance=gp_organisation)
        if user_formset.is_valid() and bank_details_form.is_valid() and surgery_email_form.is_valid():
            created_user_list = []
            surgery_email = surgery_email_form.save()
            create_gp_payments_fee(bank_details_form, gp_organisation)
            update_gp_organisation_bank_details(bank_details_form, gp_organisation)
            create_gp_user(gp_organisation)
            if surgery_email.organisation_email:
                html_message = loader.render_to_string('onboarding/surgery_email.html')
                send_mail(
                    'Thank you for setting up',
                    '',
                    settings.DEFAULT_FROM,
                    [surgery_email.organisation_email],
                    fail_silently=True,
                    html_message=html_message,
                )
            for user in user_formset:
                if user.is_valid() and user.cleaned_data:
                    created_user_dict = create_gp_user(gp_organisation, user_form=user.cleaned_data)
                    if created_user_dict:
                        created_user_list.append(created_user_dict)

            for user in created_user_list:
                html_message = loader.render_to_string('onboarding/emr_setup_2_email.html', {
                    'user_email': user['general_pratice_user'].user.email,
                    'user_password': user['password']
                })
                send_mail(
                    'eMR Account Information',
                    '',
                    settings.DEFAULT_FROM,
                    [user['general_pratice_user'].user.email],
                    fail_silently=True,
                    html_message=html_message,
                )
            messages.success(request, 'Create User Successful!')
            login_link = request.build_absolute_uri(reverse('login',))
            welcome_message1 = 'Onboarding Successful!'
            welcome_message2 = 'Welcome to the eMR System'
            return render(request, 'onboarding/emr_message.html', {
                'welcome_message1': welcome_message1,
                'welcome_message2': welcome_message2,
                'login_link': login_link,
            })

    return render(request, 'onboarding/emr_setup_stage_2.html', {
        'surgery_form': surgery_form,
        'user_formset': user_formset,
        'bank_details_form': bank_details_form,
        'surgery_email_form': surgery_email_form
    })


def get_code_autocomplete(request):
    data = list()
    search = request.GET.get('search', '')
    if search:
        code_gps = GpPractices.objects.filter(sitenumber_c__startswith=search)
    else:
        code_gps = GpPractices.objects.all()[:10]

    if code_gps.exists():
        for code_gp in code_gps:
            data.append(code_gp.sitenumber_c)
    return JsonResponse(data, safe=False)


def get_name_autocomplete(request):
    data = list()
    search = request.GET.get('search', '')
    if search:
        name_gps = GpPractices.objects.filter(name__startswith=search)
    else:
        name_gps = GpPractices.objects.all()[:10]

    if name_gps.exists():
        for name_gp in name_gps:
            data.append(name_gp.name)

    return JsonResponse(data, safe=False)


def ajax_emis_polling(request, practice_code):
    data = {
        'status': 401,
        'practice_code': ''
    }
    gp_organisation = OrganisationGeneralPractice.objects.filter(practcode=practice_code).first()
    if gp_organisation:
        status = GetEmisStatusCode(gp_organisation=gp_organisation).call()
        data['status'] = status
        data['practice_code'] = gp_organisation.practcode

    return JsonResponse(data, safe=False)


def send_email_emr(request, emr):
    from_email = settings.DEFAULT_FROM
    to_list = [emr.pm_email]
    html_message = loader.render_to_string('onboarding/emr_email.html',{
        'link': '{}/onboarding/emr-setup-stage-2/{}'.format(request.get_host(), emr.id)
    })
    send_mail('Completely eMR', '', from_email, to_list, fail_silently=True, html_message=html_message)


def send_email_pm(request, emr):
    from_email = settings.DEFAULT_FROM
    to_list = [emr.pm_email]
    html_message = loader.render_to_string('onboarding/emr_email_PM.html')
    send_mail('Completely eMR', '', from_email, to_list, fail_silently=True, html_message=html_message)

