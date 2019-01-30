from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.db.models import Q
from django.contrib import messages

from instructions.models import Instruction
from .models import PatientReportAuth, ThirdPartyAuthorisation
from .forms import AccessCodeForm, ThirdPartyAuthorisationForm
from .functions import validate_pin
from report.mobile import AuthMobile

import json
import datetime


def sar_request_code(request, instruction_id, access_type, url):
    error_message = None
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    third_party_authorisation = None
    if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
        patient_auth = get_object_or_404(PatientReportAuth, url=url)
        greeting_name = patient_auth.patient.user.first_name
        if patient_auth.locked_report:
            return redirect_auth_limit(request)
    else:
        third_party_authorisation = get_object_or_404(ThirdPartyAuthorisation, unique=url)
        patient_auth = third_party_authorisation.patient_report_auth
        greeting_name = third_party_authorisation.company
        if third_party_authorisation.expired:
            return render(request, 'date_expired.html', )

        if third_party_authorisation.locked_report:
            return redirect_auth_limit(request)

    if request.method == 'POST':
        third_party_response_sms = None
        third_party_response_voice = None
        successful_request = False
        if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
            patient_auth.count = 0
            patient_response_sms = AuthMobile(number=instruction.patient_information.get_telephone_e164()).request()
            if patient_response_sms and patient_response_sms.status_code == 200:
                response_results_dict = json.loads(patient_response_sms.text)
                patient_auth.mobi_request_id = response_results_dict['id']
                successful_request = True
            patient_auth.save()
        else:
            third_party_authorisation.count = 0
            if third_party_authorisation.family_phone_number:
                third_party_response_sms = AuthMobile(number=third_party_authorisation.get_family_phone_e164()).request()

            if third_party_authorisation.office_phone_number:
                third_party_response_voice = AuthMobile(number=third_party_authorisation.get_office_phone_e164(), type='ivr').request()

            if third_party_response_sms and third_party_response_sms.status_code == 200:
                response_results_dict = json.loads(third_party_response_sms.text)
                third_party_authorisation.mobi_request_id = response_results_dict['id']
                successful_request = True

            if third_party_response_voice and third_party_response_voice.status_code == 200:
                response_results_dict = json.loads(third_party_response_voice.text)
                third_party_authorisation.mobi_request_voice_id = response_results_dict['id']
                successful_request = True
            third_party_authorisation.save()

        if successful_request:
            return redirect('report:access-code', access_type=access_type, url=url)
        else:
            error_message = "Something went wrong"

    return render(request, 'patient/auth_1.html', {
        'name': greeting_name,
        'message': error_message
    })


def sar_access_code(request, access_type, url):
    access_code_form = AccessCodeForm()
    error_message = None
    if url:
        if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
            patient_auth = PatientReportAuth.objects.filter(url=url).first()
            if patient_auth.locked_report:
                return redirect_auth_limit(request)
            instruction = patient_auth.instruction
            patient_phone = instruction.patient_information.get_telephone_e164()

            number_1 = ["*"] * (len(patient_phone) - 2)
            number_1.append(patient_phone[-2:])
            number_1 = " ".join(map(str, number_1))

            number_2 = ''
        else:
            third_party_authorisation = get_object_or_404(ThirdPartyAuthorisation, unique=url)
            patient_auth = third_party_authorisation.patient_report_auth
            if third_party_authorisation.expired:
                return render(request, 'date_expired.html', )

            if third_party_authorisation.locked_report:
                return redirect_auth_limit(request)
            third_party_family_phone = third_party_authorisation.get_family_phone_e164()
            third_party_office_phone = third_party_authorisation.get_office_phone_e164()

            number_1 = ["*"] * (len(third_party_family_phone) - 2)
            number_1.append(third_party_family_phone[-2:])
            number_1 = " ".join(map(str, number_1))

            number_2 = ["*"] * (len(third_party_office_phone) - 2)
            number_2.append(third_party_office_phone[-2:])
            number_2 = " ".join(map(str, number_2))

        if request.method == 'POST':
            third_party_response_sms = None
            third_party_response_sms_voice = None
            if request.POST.get('button') == 'Request New Code':
                if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
                    patient_response_sms = AuthMobile(number=patient_phone).request()
                    if patient_response_sms and patient_response_sms.status_code == 200:
                        response_results_dict = json.loads(patient_response_sms.text)
                        patient_auth.mobi_request_id = response_results_dict['id']
                        patient_auth.save()
                else:
                    if third_party_authorisation.family_phone_number:
                        third_party_response_sms = AuthMobile(number=third_party_family_phone).request()

                    if third_party_authorisation.office_phone_number:
                        third_party_response_sms_voice = AuthMobile(number=third_party_office_phone, type='ivr').request()

                    if third_party_response_sms and third_party_response_sms.status_code == 200:
                        response_results_dict = json.loads(third_party_response_sms.text)
                        third_party_authorisation.mobi_request_id = response_results_dict['id']

                    if third_party_response_sms_voice and third_party_response_sms_voice.status_code == 200:
                        response_results_dict = json.loads(third_party_response_sms_voice.text)
                        third_party_authorisation.mobi_request_voice_id = response_results_dict['id']

                    third_party_authorisation.save()
            else:
                success_voice_pin = False
                report_auth = request.POST.get('access_code')
                if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
                    patient_response_sms = AuthMobile(
                        mobi_id=patient_auth.mobi_request_id,
                        pin=report_auth
                    ).verify()
                    success_sms_pin = validate_pin(patient_response_sms, report_auth, patient_auth, access_type)
                else:
                    third_party_response_sms = AuthMobile(
                        mobi_id=third_party_authorisation.mobi_request_id, pin=report_auth
                    ).verify()

                    third_party_response_sms_voice = AuthMobile(
                        mobi_id=third_party_authorisation.mobi_request_voice_id, pin=report_auth
                    ).verify()
                    success_sms_pin = validate_pin(
                        third_party_response_sms, report_auth, patient_auth, access_type,
                        third_party_authorisation, otp_type='sms'
                    )
                    success_voice_pin = validate_pin(
                        third_party_response_sms_voice, report_auth, patient_auth, access_type,
                        third_party_authorisation, otp_type='voice'
                    )

                if success_sms_pin or success_voice_pin:
                    response = redirect('report:select-report',
                                        access_type=access_type)
                    response.set_cookie('verified_pin', report_auth)
                    return response
                else:
                    error_message = "Sorry, that code has not been recognised. Please try again."

    return render(request, 'patient/auth_2_access_code.html', {
        'form': access_code_form,
        'message': error_message,
        'name': patient_auth.patient.user.first_name,
        'number_1': str(number_1),
        'number_2': str(number_2)
    })


def get_report(request, access_type):
    if not request.COOKIES.get('verified_pin'):
        return redirect('report:session-expired')

    verified_pin = request.COOKIES.get('verified_pin')
    third_parties = None
    if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
        report_auth = get_object_or_404(PatientReportAuth, verify_pin=verified_pin)
        third_parties = report_auth.third_parties.all()
        if report_auth.locked_report:
            return redirect_auth_limit(request)
    elif access_type == PatientReportAuth.ACCESS_TYPE_THIRD_PARTY:
        third_party_authorisation = ThirdPartyAuthorisation.objects.get(
            Q(verify_sms_pin=verified_pin) | Q(verify_voice_pin=verified_pin)
        )
        report_auth = third_party_authorisation.patient_report_auth

        if third_party_authorisation.expired:
            return render(request, 'date_expired.html', )

        if third_party_authorisation.locked_report:
            return redirect_auth_limit(request)

    if request.method == 'POST':
            instruction = get_object_or_404(Instruction, id=report_auth.instruction_id)

            if request.POST.get('button') == 'Download Report':
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="medical_report.pdf"'
                response.write(instruction.medical_report.read())
                return response

            elif request.POST.get('button') == 'View Report':
                return HttpResponse(instruction.medical_report, content_type='application/pdf')

            elif request.POST.get('button') == 'Print Report':
                return HttpResponse(instruction.medical_report, content_type='application/pdf')

    return render(request, 'patient/auth_4_select_report.html',{
        'verified_pin': verified_pin,
        'report_auth': report_auth,
        'third_parties': third_parties,
        'access_type': access_type,
    })


def redirect_auth_limit(request):
    error_message = 'You exceeded the limit'
    return render(request, 'patient/auth_3_exceed_limit.html', {'message': error_message})


def session_expired(request):
    return render(request, 'patient/session_expired.html')


def add_third_party_authorisation(request, report_auth_id):
    report_auth = get_object_or_404(PatientReportAuth, id=report_auth_id)
    third_party_form = ThirdPartyAuthorisationForm()

    if request.method == 'POST':
        third_party_form = ThirdPartyAuthorisationForm(request.POST)
        if third_party_form.is_valid():
            third_party_authorisation = third_party_form.save(report_auth)
            send_mail(
                'Medical Report Authorisation',
                'Your access on SAR report from {patient_name} has been initiated. Please click {link} to access the report'.format(
                    patient_name=report_auth.patient.user.first_name,
                    link=request.scheme + '://' + request.get_host() + reverse(
                        'report:request-code', kwargs={
                            'instruction_id': report_auth.instruction.id,
                            'access_type': PatientReportAuth.ACCESS_TYPE_THIRD_PARTY,
                            'url': third_party_authorisation.unique
                        }
                    )
                ),
                'Medidata',
                [third_party_authorisation.email],
                fail_silently=True
            )

            return redirect('report:select-report', access_type=PatientReportAuth.ACCESS_TYPE_PATIENT)

    return render(request, 'patient/add_third_authorise.html', {
        'third_party_form': third_party_form
    })


def cancel_authorisation(request, third_party_authorisation_id):
    third_party_authorisation = get_object_or_404(ThirdPartyAuthorisation, id=third_party_authorisation_id)
    report_auth = third_party_authorisation.patient_report_auth

    third_party_authorisation.expired_date = datetime.datetime.now().date()
    third_party_authorisation.expired = True
    third_party_authorisation.locked_report = False
    third_party_authorisation.save()

    send_mail(
        'Medical Report Authorisation',
        'Your access on SAR report from {patient_name} has been expired. Please contact {patient_name}'.format(
            patient_name=report_auth.patient.user.first_name,
        ),
        'Medidata',
        [third_party_authorisation.email],
        fail_silently=True
    )

    return redirect('report:select-report', access_type=PatientReportAuth.ACCESS_TYPE_PATIENT)


def extend_authorisation(request, third_party_authorisation_id):
    third_party_authorisation = get_object_or_404(ThirdPartyAuthorisation, id=third_party_authorisation_id)
    report_auth = third_party_authorisation.patient_report_auth

    expired_date = third_party_authorisation.expired_date + datetime.timedelta(days=30)
    limit_extend = third_party_authorisation.created + datetime.timedelta(days=360)
    if expired_date < limit_extend.date():
        third_party_authorisation.expired_date = expired_date
        third_party_authorisation.save()
        send_mail(
            'Medical Report Authorisation',
            'Your access on SAR report from {patient_name} has been extended. Please click {link} to access the report'.format(
                patient_name=report_auth.patient.user.first_name,
                link=request.scheme + '://' + request.get_host() + reverse(
                    'report:request-code', kwargs={
                        'instruction_id': report_auth.instruction.id,
                        'access_type': PatientReportAuth.ACCESS_TYPE_THIRD_PARTY,
                        'url': third_party_authorisation.unique
                    }
                )
            ),
            'Medidata',
            [third_party_authorisation.email],
            fail_silently=True
        )
    else:
        messages.error(request, 'limit exceeded')

    return redirect('report:select-report', access_type=PatientReportAuth.ACCESS_TYPE_PATIENT)


def renew_authorisation(request, third_party_authorisation_id):
    third_party_authorisation = get_object_or_404(ThirdPartyAuthorisation, id=third_party_authorisation_id)

    third_party_authorisation.expired_date = datetime.datetime.now().date() + datetime.timedelta(days=30)
    third_party_authorisation.expired = False
    third_party_authorisation.save()

    return redirect('report:select-report', access_type=PatientReportAuth.ACCESS_TYPE_PATIENT)