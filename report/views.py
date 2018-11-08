import requests
import secrets
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from medicalreport.models import AmendmentsForRecord
from services.emisapiservices import services
from medicalreport.reports import MedicalReport
from services.xml.medical_report_decorator import MedicalReportDecorator
from instructions.models import Instruction, Patient
from medicalreport.dummy_models import DummyInstruction
from .models import PatientReportAuth
from .forms import AccessCodeForm


def sar_request_code(request, instruction_id, url):
    """
    send sms to patient
    :param request:
    :return:
    """
    error_message = None
    get_object_or_404(Instruction, pk=instruction_id)
    patient_auth = get_object_or_404(PatientReportAuth, url=url)
    if request.method == 'POST':
        patient_auth.count = 0
        patient_auth.save()
        response = requests.post(
            "https://api.checkmobi.com/v1/validation/request",
            data=json.dumps({"number": "+66972988662", "type": "sms", "platform": "web"}),
            headers={
                "Authorization": "C2F45334-A46E-44E1-9294-16F5A7F777A9",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        if response.status_code == 200:
            response_results_dict = json.loads(response.text)
            patient_auth.mobi_request_id = response_results_dict['id']
            patient_auth.save()
            return redirect('report:access-code')
        else:
            error_message = "Something went wrong"
    return render(request, 'patient/auth_1.html', {
        'name': patient_auth.patient.user.first_name,
        'link': '',
        'message': error_message
    })


def sar_access_code(request,  **kawrgs,):
    access_code_form = AccessCodeForm
    error_message = (kawrgs.get('messages') if kawrgs.get('messages') else None)

    number = ["*"] * (len('+66972988662') - 2)
    number.append('+66972988662'[:2])
    number = " ".join(map(str, number))
    patient_auth = PatientReportAuth.objects.last()
    if request.method == 'POST':
        if request.POST.get('button') == 'Request New Code':
            response = requests.post(
                "https://api.checkmobi.com/v1/validation/request",
                data=json.dumps({"number": "+66972988662", "type": "sms", "platform": "web"}),
                headers={
                    "Authorization": "C2F45334-A46E-44E1-9294-16F5A7F777A9",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
        else:
            patient_auth.count = patient_auth.count + 1
            patient_auth.save()
            if patient_auth.count >= 3:
                error_message = 'You exceeded the limit'
                return render(request, 'patient/auth_3_exceed_limit.html', {'message': error_message})
            report_auth = request.POST.get('access_code')
            response = requests.post(
                "https://api.checkmobi.com/v1/validation/verify",
                data=json.dumps({"id": patient_auth.mobi_request_id, "pin": report_auth}),
                headers={
                    "Authorization": "C2F45334-A46E-44E1-9294-16F5A7F777A9",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            if response.status_code == 200:
                response_results_dict = json.loads(response.text)
                if response_results_dict['validated']:
                    patient_auth.verify_pin = report_auth
                    patient_auth.save()
                    return redirect('report:select-report',  report_auth)
                else:
                    error_message = "Sorry, that code has not been recognised. Please try again."
    return render(request, 'patient/auth_2_access_code.html', {
        'form': access_code_form,
        'message': error_message,
        'name': patient_auth.patient.user.first_name,
        'number': str(number)
    })


@login_required(login_url='/accounts/login')
def get_report(request, **kwargs):
    if 'verified_pin' not in kwargs:
        error_message = "try again"
        return redirect('report:access-code', error_message)
    if request.method == 'POST':
        try:
            report_auth = PatientReportAuth.objects.get(verify_pin=kwargs['verified_pin'])
            instruction = get_object_or_404(Instruction, id=report_auth.instruction_id)
            redaction = get_object_or_404(AmendmentsForRecord, instruction=report_auth.instruction_id)

            raw_xml = services.GetMedicalRecord(redaction.patient_emis_number).call()
            medical_record_decorator = MedicalReportDecorator(raw_xml, instruction)
            dummy_instruction = DummyInstruction(instruction)
            gp_name = redaction.get_gp_name

            params = {
                'medical_record': medical_record_decorator,
                'redaction': redaction,
                'instruction': instruction,
                'gp_name': gp_name,
                'dummy_instruction': dummy_instruction
            }
            if request.POST.get('button') == 'Download Report':
                return MedicalReport.download(params)

            elif request.POST.get('button') == 'View Report':
                return MedicalReport.render(params)

            elif request.POST.get('button') == 'Print Report':
                return render(request, 'medicalreport/reports/medicalreport.html', params)

        except PatientReportAuth.DoesNotExist:
            raise Http404("Invalid token")
    return render(request, 'patient/auth_4_select_report.html')
