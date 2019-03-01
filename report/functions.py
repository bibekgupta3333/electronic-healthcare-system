
from django.core.mail import send_mail
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from zipfile import ZipFile, ZIP_DEFLATED
from .models import PatientReportAuth

import json

#todo add link
def send_patient_mail(patient, gp_practice):
    send_mail(
        'Completely eMR',
        'Your instruction has been submitted',
        'MediData',
        [patient.email],
        fail_silently=True,
        html_message=loader.render_to_string('medicalreport/patient_email.html', {
            'gp': gp_practice.name,
            'link': 'just a link'
        })
    )


def validate_pin(response, pin,  patient_auth, access_type, third_party_authorisation=None, otp_type=''):
    max_input = 3
    if response.status_code == 200:
        response_results_dict = json.loads(response.text)
        if access_type == PatientReportAuth.ACCESS_TYPE_PATIENT:
            if response_results_dict['validated']:
                patient_auth.verify_pin = pin
                patient_auth.count = 0
                patient_auth.save()
                return True
            else:
                patient_auth.count = patient_auth.count + 1
                if patient_auth.count >= max_input:
                    patient_auth.locked_report = True
                    patient_auth.count = 0
                patient_auth.save()
        elif access_type == PatientReportAuth.ACCESS_TYPE_THIRD_PARTY:
            if response_results_dict['validated']:
                if otp_type == 'sms':
                    third_party_authorisation.verify_sms_pin = pin
                elif otp_type == 'voice':
                    third_party_authorisation.verify_voice_pin = pin
                third_party_authorisation.count = 0
                third_party_authorisation.save()
                return True
            else:
                third_party_authorisation.count = third_party_authorisation.count + 1
                if third_party_authorisation.count >= max_input:
                    third_party_authorisation.locked_report = True
                    third_party_authorisation.count = 0
                third_party_authorisation.save()
    return False


def get_zip_medical_report(instruction):
    path_patient = instruction.patient_information.__str__()
    path = settings.MEDIA_ROOT + '/patient_attachments/' + path_patient + '/'
    attachments = instruction.download_attachments
    with ZipFile(path + 'medicalreports.zip','w', ZIP_DEFLATED) as zip:
        zip.write(instruction.medical_with_attachment_report.path, 'medical_report.pdf')
        for attachment in attachments.split(','):
            zip.write(path + attachment, attachment)
    return open(path + 'medicalreports.zip', 'rb')
