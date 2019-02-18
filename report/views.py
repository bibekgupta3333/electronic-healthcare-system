from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from django.db.models import Sum, Q

from instructions.model_choices import *
from accounts.models import *

from django.core.mail import send_mail
from django.contrib import messages
from django.template import loader

from instructions.models import Instruction
from .models import PatientReportAuth, ThirdPartyAuthorisation
from .forms import AccessCodeForm, ThirdPartyAuthorisationForm
from .functions import validate_pin
from services.xml.base64_attachment import Base64Attachment
from medicalreport.models import AmendmentsForRecord
from services.xml.medical_report_decorator import MedicalReportDecorator
from services.emisapiservices import services
from report.mobile import AuthMobile
from django.conf import settings
from PIL import Image

import io
import json
import datetime
import PyPDF2
import subprocess
import img2pdf
import reportlab
import reportlab.lib.pagesizes as pdf_sizes
import logging

logger = logging.getLogger(__name__)


def sar_request_code(request, instruction_id, access_type, url):
    error_message = None
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    third_party_authorisation = None

    if instruction.deactivated:
        return render(request, 'de_activate.html', )
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
        'message': error_message,
        'access_type': access_type,
        'third_party_authorisation': third_party_authorisation,
    })


def sar_access_code(request, access_type, url):
    access_code_form = AccessCodeForm()
    error_message = None
    third_party_authorisation = None
    if url:
        if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
            patient_auth = PatientReportAuth.objects.filter(url=url).first()
            if patient_auth.locked_report:
                return redirect_auth_limit(request)
            instruction = patient_auth.instruction
            patient_phone = instruction.patient_information.get_telephone_e164()

            number = ["*"] * (len(patient_phone) - 3)
            number.append(patient_phone[-3:])
            number = " ".join(map(str, number))
        else:
            third_party_authorisation = get_object_or_404(ThirdPartyAuthorisation, unique=url)
            patient_auth = third_party_authorisation.patient_report_auth
            if third_party_authorisation.expired:
                return render(request, 'date_expired.html', )

            if third_party_authorisation.locked_report:
                return redirect_auth_limit(request)
            phone_number = ''
            if third_party_authorisation.office_phone_number:
                phone_number = third_party_authorisation.get_office_phone_e164()
            elif third_party_authorisation.family_phone_number:
                phone_number = third_party_authorisation.get_family_phone_e164()

            if phone_number:
                number = ["*"] * (len(phone_number) - 3)
                number.append(phone_number[-3:])
                number = " ".join(map(str, number))

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
                        third_party_response_sms = AuthMobile(number=phone_number).request()

                    if third_party_authorisation.office_phone_number:
                        third_party_response_sms_voice = AuthMobile(number=phone_number, type='ivr').request()

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
                    if patient_auth.locked_report:
                        return redirect_auth_limit(request)
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

                    if third_party_authorisation.locked_report:
                        return redirect_auth_limit(request)

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
        'number': str(number),
        'access_type': access_type,
        'third_party_authorisation': third_party_authorisation,
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
                response = get_merged_medicalreport_attachment(instruction_id=instruction.id)
                response['Content-Disposition'] = 'attachment; filename="medical_report.pdf"'
                return response

            elif request.POST.get('button') == 'View Report':
                return get_merged_medicalreport_attachment(instruction_id=instruction.id)

            elif request.POST.get('button') == 'Print Report':
                return get_merged_medicalreport_attachment(instruction_id=instruction.id)

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

def summry_report(request):
    if 'current_year' in request.GET:
        numYear = int(request.GET.get('current_year', None))
    else:
        numYear = datetime.datetime.now().year

    title = 'Reporting - ' + str(numYear)
    numMonth = 1
    newList = list()
    progressList = list()

    if request.user.type == CLIENT_USER:
        completeList = list()
        rejectList = list()
        paidList = list()
        client = ClientUser.objects.filter(organisation = request.user.get_my_organisation()).first()

        gpSumInt = 0
        mediSumInt = 0

        while numMonth <= 12:
            newQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_NEW, created__month = numMonth, created__year = numYear, \
                                                        client_user = client).count()
            progressQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_PROGRESS, created__month = numMonth, created__year = numYear, \
                                                        client_user = client).count()
            completeQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_COMPLETE, completed_signed_off_timestamp__month = numMonth,\
                                                            completed_signed_off_timestamp__year = numYear, client_user = client).count()
            rejectQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_REJECT, rejected_timestamp__month = numMonth,\
                                                            rejected_timestamp__year = numYear, client_user = client).count()

            gpSumInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_COMPLETE, completed_signed_off_timestamp__month = numMonth, \
                                                        completed_signed_off_timestamp__year = numYear, client_user = client).aggregate(Sum('gp_earns'))
            mediSumInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_COMPLETE, completed_signed_off_timestamp__month = numMonth, \
                                                        completed_signed_off_timestamp__year = numYear, client_user = client).aggregate(Sum('medi_earns'))

            if (gpSumInt.get('gp_earns__sum') != None) and (mediSumInt.get('medi_earns__sum') != None):
                paidSum = gpSumInt.get('gp_earns__sum') + mediSumInt.get('medi_earns__sum')
            else:
                paidSum = 0

            newList.append(newQueryInt)
            progressList.append(progressQueryInt)
            completeList.append(completeQueryInt)
            rejectList.append(rejectQueryInt)

            paidList.append(float(paidSum))
            numMonth = numMonth + 1
            
        return render(request, 'reporting/summary_report.html', {
                    'header_title': title,
                    'currentYear' : numYear,
                    'previousYear' : numYear - 1,
                    'nextYear' : numYear + 1,
                    'newList' : newList,
                    'progressList' : progressList,
                    'completeList' : completeList,
                    'rejectList' : rejectList,
                    'paidList' : paidList
                })

    SARSlist = list()
    AMRAlist = list()
    incomeList = list()
    gp_pratice = request.user.get_my_organisation()
    
    while numMonth <= 12:
        SARSqueryInt = Instruction.objects.filter(type = SARS_TYPE, gp_practice_id = gp_pratice, created__month = numMonth, created__year = numYear).count()
        AMRAqueryInt = Instruction.objects.filter(type = AMRA_TYPE, gp_practice_id = gp_pratice, created__month = numMonth, created__year = numYear).count()

        newQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_NEW, created__month = numMonth, created__year = numYear, \
                                                    gp_practice_id = gp_pratice).count()
        progressQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_PROGRESS, created__month = numMonth, created__year = numYear, \
                                                    gp_practice_id = gp_pratice).count()

        incomeQueryInt = Instruction.objects.filter(status = INSTRUCTION_STATUS_COMPLETE, completed_signed_off_timestamp__month = numMonth, \
                                                    completed_signed_off_timestamp__year = numYear, gp_practice_id = gp_pratice).aggregate(Sum('gp_earns'))
        incomeInt = float(incomeQueryInt.get('gp_earns__sum')) if incomeQueryInt.get('gp_earns__sum') != None else 0

        SARSlist.append(SARSqueryInt)
        AMRAlist.append(AMRAqueryInt)
        newList.append(newQueryInt)
        progressList.append(progressQueryInt)
        incomeList.append(incomeInt)

        numMonth = numMonth + 1

    return render(request, 'reporting/summary_report_gp.html', {
                    'header_title': title,
                    'currentYear' : numYear,
                    'previousYear' : numYear - 1,
                    'nextYear' : numYear + 1,
                    'SARSlist' : SARSlist,
                    'AMRAlist' : AMRAlist,
                    'newList' : newList,
                    'progressList' : progressList,
                    'incomeList' : incomeList
                })

def add_third_party_authorisation(request, report_auth_id):
    report_auth = get_object_or_404(PatientReportAuth, id=report_auth_id)
    third_party_form = ThirdPartyAuthorisationForm()

    if request.method == 'POST':
        third_party_form = ThirdPartyAuthorisationForm(request.POST)
        if third_party_form.is_valid():
            third_party_authorisation = third_party_form.save(report_auth)
            phone_number = ''
            if third_party_authorisation.office_phone_number:
                phone_number = third_party_authorisation.get_office_phone_e164()
            elif third_party_authorisation.family_phone_number:
                phone_number = third_party_authorisation.get_family_phone_e164()

            if phone_number:
                last_three_digits = phone_number[-3:]

            send_mail(
                'Completed SAR Request',
                '',
                'Medidata',
                [third_party_authorisation.email],
                fail_silently=True,
                html_message=loader.render_to_string('third_parties_email.html', {
                    'patient_first_name': report_auth.instruction.patient_information.patient_first_name,
                    'report_link': request.scheme + '://' + request.get_host() + reverse(
                        'report:request-code', kwargs={
                            'instruction_id': report_auth.instruction.id,
                            'access_type': PatientReportAuth.ACCESS_TYPE_THIRD_PARTY,
                            'url': third_party_authorisation.unique
                        }),
                    'last_three_digits': last_three_digits
                })
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
            patient_name=report_auth.instruction.patient_information.patient_first_name,
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
                patient_name=report_auth.instruction.patient_information.patient_first_name,
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


def get_merged_medicalreport_attachment(instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)
    redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)

    patient_emis_number = instruction.patient_information.patient_emis_number
    raw_xml_or_status_code = services.GetMedicalRecord(patient_emis_number, instruction.gp_practice).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    medical_record_decorator = MedicalReportDecorator(raw_xml_or_status_code, instruction)
    output = PyPDF2.PdfFileWriter()

    # add each page of medical report to output file
    medical_report = PyPDF2.PdfFileReader(instruction.medical_report)
    for page_num in range(medical_report.getNumPages()):
        output.addPage(medical_report.getPage(page_num))

    # create list of PdfFileReader obj from raw bytes of xml data
    attachments_pdf = []
    for attachment in medical_record_decorator.attachments():
        xpaths = attachment.xpaths()
        if redaction.redacted(xpaths) is not True:
            raw_xml_or_status_code = services.GetAttachment(
                instruction.patient_information.patient_emis_number,
                attachment.dds_identifier(),
                gp_organisation=instruction.gp_practice).call()
            if isinstance(raw_xml_or_status_code, int):
                return redirect('services:handle_error', code=raw_xml_or_status_code)

            file_name = Base64Attachment(raw_xml_or_status_code).filename()
            file_type = file_name.split('.')[-1]
            raw_attachment = Base64Attachment(raw_xml_or_status_code).data()
            buffer = io.BytesIO(raw_attachment)
            folder = settings.BASE_DIR + '/static/generic_pdf/'
            try:
                if file_type == 'pdf':
                    attachments_pdf.append(PyPDF2.PdfFileReader(buffer))
                elif file_type in ['doc', 'docx', 'rtf']:
                    tmp_file = 'temp1.' + file_type
                    f = open(folder + tmp_file, 'wb')
                    f.write(buffer.getvalue())
                    f.close()
                    subprocess.call(
                        ("export HOME=/tmp && libreoffice --headless --convert-to pdf --outdir " + folder + " " + folder + "/" + tmp_file),
                        shell=True
                    )
                    pdf = open(folder + 'temp1.pdf', 'rb')
                    attachments_pdf.append(PyPDF2.PdfFileReader(pdf))
                elif file_type in ['jpg', 'jpeg', 'png', 'tiff']:
                    image = Image.open(buffer)
                    image_format = image.format
                    if image_format == "TIFF":
                        max_pages = 200
                        height = image.tag[0x101][0]
                        width = image.tag[0x100][0]
                        out_pdf_io = io.BytesIO()
                        c = reportlab.pdfgen.canvas.Canvas(out_pdf_io, pagesize=pdf_sizes.letter)
                        pdf_width, pdf_height = pdf_sizes.letter
                        page = 0
                        while True:
                            try:
                                image.seek(page)
                            except EOFError:
                                break
                            if pdf_width * height / width <= pdf_height:
                                c.drawInlineImage(image, 0, 0, pdf_width, pdf_width * height / width)
                            else:
                                c.drawInlineImage(image, 0, 0, pdf_height * width / height, pdf_height)
                            c.showPage()
                            if max_pages and page > max_pages:
                                break
                            page += 1
                        c.save()
                        attachments_pdf.append(PyPDF2.PdfFileReader(out_pdf_io))
                    else:
                        pdf_bytes = img2pdf.convert('imgtemp1.pdf')
                        f = open(folder + 'imgtemp1.pdf', 'wb')
                        f.write(pdf_bytes)
                        attachments_pdf.append(PyPDF2.PdfFileReader(f))
                        image.close()
                        f.close()
            except Exception as e:
                logger.error(e)

    # add each page of each attachment to output file
    for pdf in attachments_pdf:
        if pdf.isEncrypted:
            pdf.decrypt(password='')
        for page_num in range(pdf.getNumPages()):
            output.addPage(pdf.getPage(page_num))

    pdf_page_buf = io.BytesIO()
    output.write(pdf_page_buf)

    response = HttpResponse(
        pdf_page_buf.getvalue(),
        content_type="application/pdf",
    )
    return response
