import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from instructions.models import Instruction
from .models import PatientReportAuth
from .forms import AccessCodeForm
from report.mobile import AuthMobile


def sar_request_code(request, instruction_id, url):
    error_message = None
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    patient_auth = get_object_or_404(PatientReportAuth, url=url)
    if patient_auth.locked_report:
        return redirect_auth_limit(request)
    if request.method == 'POST':
        patient_auth.count = 0
        patient_auth.save()
        response = AuthMobile(number=instruction.patient_information.get_telephone_e164()).request()

        if response.status_code == 200:
            response_results_dict = json.loads(response.text)
            patient_auth.mobi_request_id = response_results_dict['id']
            patient_auth.save()
            return redirect('report:access-code', url=url)
        else:
            error_message = "Something went wrong"
    return render(request, 'patient/auth_1.html', {
        'name': patient_auth.patient.user.first_name,
        'link': '',
        'message': error_message
    })


def sar_access_code(request, url):
    access_code_form = AccessCodeForm
    error_message = None
    max_input = 3

    if url:
        patient_auth = PatientReportAuth.objects.filter(url=url).first()
        instruction = patient_auth.instruction
        patient_phone = instruction.patient_information.get_telephone_e164()
        if patient_auth.locked_report:
            return redirect_auth_limit(request)
        number = ["*"] * (len(patient_phone) - 2)
        number.append(patient_phone[-2:])
        number = " ".join(map(str, number))
        if request.method == 'POST':
            if request.POST.get('button') == 'Request New Code':
                response = AuthMobile(number=patient_phone).request()
                if response.status_code == 200:
                    response_results_dict = json.loads(response.text)
                    patient_auth.mobi_request_id = response_results_dict['id']
                    patient_auth.save()
            else:
                report_auth = request.POST.get('access_code')
                response = AuthMobile(mobi_id=patient_auth.mobi_request_id, pin=report_auth).verify()
                if response.status_code == 200:
                    response_results_dict = json.loads(response.text)
                    if response_results_dict['validated']:
                        patient_auth.verify_pin = report_auth
                        patient_auth.count = 0
                        patient_auth.save()
                        response = redirect('report:select-report')
                        response.set_cookie('verified_pin', report_auth)
                        return response
                    else:
                        patient_auth.count = patient_auth.count + 1
                        if patient_auth.count >= max_input:
                            patient_auth.locked_report = True
                            patient_auth.count = 0
                        patient_auth.save()
                        error_message = "Sorry, that code has not been recognised. Please try again."
    return render(request, 'patient/auth_2_access_code.html', {
        'form': access_code_form,
        'message': error_message,
        'name': patient_auth.patient.user.first_name,
        'number': str(number)
    })


def get_report(request):
    if not request.COOKIES.get('verified_pin'):
        return redirect('report:session-expired')

    verified_pin = request.COOKIES.get('verified_pin')

    try:
        report_auth = PatientReportAuth.objects.get(verify_pin=verified_pin)
        if report_auth.locked_report:
            return redirect_auth_limit(request)
    except PatientReportAuth.DoesNotExist:
        raise Http404("Invalid token")

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
        'name': report_auth.patient.user.first_name
    })


def redirect_auth_limit(request):
    error_message = 'You exceeded the limit'
    return render(request, 'patient/auth_3_exceed_limit.html', {'message': error_message})


def session_expired(request):
    return render(request, 'patient/session_expired.html')
