from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.core.mail import send_mail
from instructions.models import Setting
from django.conf import settings
from django.forms import formset_factory
from django.contrib import messages
from .functions import *
from .forms import *


@login_required(login_url='/accounts/login')
def emr_setup(request):
    emr_form = EMRSetupForm()
    created = False

    if request.method == "POST":
        emr_form = EMRSetupForm(request.POST)
        if emr_form.is_valid():
            emr = emr_form.save()
            send_email_emr(request, emr)
            send_email_pm(request, emr)
            created = True

    return render(request, 'onboarding/emr_setup.html', {
        'emr_form': emr_form,
        'created': created
    })


def send_email_emr(request, emr):
    setting = Setting.objects.all().first()
    if setting:
        from_email = settings.DEFAULT_FROM
        to_list = [emr.pm_email]
        html_message = loader.render_to_string('onboarding/emr_email.html',{
            'link': '{}/onboarding/emr_setup_stage_2/{}'.format(setting.site, emr.id)
        })
        send_mail('Completely eMR','',from_email,to_list,fail_silently=True,html_message=html_message)


def send_email_pm(request, emr):
    from_email = settings.DEFAULT_FROM
    to_list = [emr.pm_email]
    html_message = loader.render_to_string('onboarding/emr_email_PM.html')
    send_mail('Completely eMR', '', from_email, to_list, fail_silently=True, html_message=html_message)


def emr_setup_stage_2(request, emrsetup_id=None):
    emr_setup = get_object_or_404(EMRSetup, pk=emrsetup_id)
    address = ''
    if emr_setup.address_line1:
        address += emr_setup.address_line1
    if emr_setup.address_line2:
        address += ' ' + emr_setup.address_line2
    surgery_form = SurgeryEmrSetUpStage2Form(initial={
        'surgery_name': emr_setup.surgery_name,
        'surgery_code': emr_setup.surgery_code,
        'address': address,
        'postcode': emr_setup.post_code,
        'surgery_tel_number': emr_setup.phone,
        'surgery_email': emr_setup.surgery_email
    })

    UserEmrSetUpStage2Formset = formset_factory(UserEmrSetUpStage2Form, min_num=2, validate_min=True, extra=2)
    user_formset = UserEmrSetUpStage2Formset()
    bank_details_form = BankDetailsEmrSetUpStage2Form()

    if request.method == "POST":
        user_formset = UserEmrSetUpStage2Formset(request.POST)
        bank_details_form = BankDetailsEmrSetUpStage2Form(request.POST)
        if user_formset.is_valid() and bank_details_form.is_valid():
            gp_organisation = create_gp_organisation(emr_setup, bank_details_form)
            gp_payments_fee = create_gp_payments_fee(bank_details_form, gp_organisation)
            created_user_list = []
            created_manager_user_dict = create_gp_user(gp_organisation, emr_setup=emr_setup)
            if created_manager_user_dict:
                created_user_list.append(created_manager_user_dict)
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
            return redirect('instructions:view_pipeline')

    return render(request, 'onboarding/emr_setup_stage_2.html', {
        'surgery_form': surgery_form,
        'user_formset': user_formset,
        'bank_details_form': bank_details_form,
    })