import requests
import secrets

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


@login_required(login_url='/accounts/login')
def sar_request_code(request, instruction_id, url):
    """
    send sms to patient
    :param request:
    :return:
    """
    error_message = None
    get_object_or_404(Instruction, pk=instruction_id)
    import json
    if request.method == 'POST':
        token = secrets.token_urlsafe(4)
        PatientReportAuth.objects.filter(patient=Patient.objects.get(user=request.user)).delete()
        patient_auth = get_object_or_404(PatientReportAuth, url=url)
        patient_auth.token = token
        patient_auth.count = 0
        patient_auth.save()
        response = requests.post("https://api.checkmobi.com/v1/sms/send", data=json.dumps({
                                                                                "to": "+37496223340",
                                                                                "text": "hello world",
                                                                                "platform": "web",
                                                                                }),
                                 headers={
                                         "Authorization": "A86AE899-E241-430A-85D7-131D861738EF",
                                         "Content-Type": "application/json",
                                         "Accept": "application/json"
                                         }
                                 )

        if response.status_code == 200:
            return redirect('report:access-code')
        else:
            error_message = "Something went wrong"
    return render(request, 'patient/auth_1.html', {
        'name': request.user.first_name,
        'link': '',
        'message': error_message
    })


@login_required(login_url='/accounts/login')
def sar_access_code(request,  **kawrgs,):
    access_code_form = AccessCodeForm
    error_message = (kawrgs.get('messages') if kawrgs.get('messages') else None)

    number = ["*"] * (len(request.user.userprofilebase.telephone_mobile) - 2)
    number.append(request.user.userprofilebase.telephone_mobile[:2])
    number = " ".join(map(str, number))

    if request.method == 'POST':
        if request.POST.get('button') == 'Request New Code':
            token = secrets.token_urlsafe(4)
            patient_auth = PatientReportAuth.objects.last()
            patient_auth.token = token
            patient_auth.count = patient_auth.count + 1
            patient_auth.save()
            if patient_auth.count >= 3:
                error_message = 'You exceeded the limit'
                return render(request, 'patient/auth_3_exceed_limit.html', {'message': error_message})

        else:
            try:
                report_auth = PatientReportAuth.objects.get(token=request.POST.get('access_code'))
                return redirect('report:select-report',  report_auth.token)
            except PatientReportAuth.DoesNotExist:
                error_message = "Wrong access code"
    return render(request, 'patient/auth_2_access_code.html', {
        'form': access_code_form,
        'message': error_message,
        'name': request.user.first_name,
        'number': str(number)
    })


@login_required(login_url='/accounts/login')
def get_report(request, **kwargs):
    if 'token' not in kwargs:
        error_message = "try again"
        return redirect('report:access-code', error_message)
    if request.method == 'POST':
        try:
            report_auth = PatientReportAuth.objects.get(token=kwargs.get('token'))
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
