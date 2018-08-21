from django.shortcuts import render
from django.http import HttpResponse
from .emisapiservices import services
from .dummy_models import DummyPatient, DummyPractice
from .xml.patient_list import PatientList
import datetime
# Create your views here.


# purpose of the view is to test the server class
# using dummy class for patient and practice model
def get_patient_list(request):
    patient = DummyPatient('patient_first_name', 'patient_last_name', datetime.datetime.strptime('1986-09-04', "%Y-%m-%d"))
    practice = DummyPractice('MediData', '1234', '29390')

    raw_xml = services.GetPatientList(practice, patient).call()
    patients = PatientList(raw_xml).patients()

    return render(request, 'services/test.html', {
        'patients': patients,
        'xml_raw_data': raw_xml
    })


def get_patient_record(request):
    practice = DummyPractice('MediData', '1234', '29390')
    patient_number = '2820'
    raw_xml = services.GetMedicalRecord(practice, patient_number).call()

    return HttpResponse(raw_xml)


def get_patient_attachment(request):
    practice = DummyPractice('MediData', '1234', '29390')
    patient_number = '2820'
    attachment_identifier = '{5C37D79F-8DB5-4754-BBDE-43BF6AFE19DE}'
    raw_xml = services.GetAttachment(practice, patient_number, attachment_identifier).call()

    return HttpResponse(raw_xml)
