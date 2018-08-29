from django.shortcuts import render
from services.dummy_models import DummyPractice
from services.emisapiservices import services
from services.xml.medical_record import MedicalRecord

# Create your views here.


class Poll(object):
    def __init__(self):
        self.choices = ['xxx', 'yyyy', 'uuu']


class DummyClient(object):
    def __init__(self):
        self.company_name = "Insurers r us"


class DummySnomedConcept(object):
    def __init__(self, desc):
        self.fsn_description = desc


class DummyInstruction(object):
    def __init__(self):
        self.client = DummyClient()
        self.selected_snomed_concepts = [
            DummySnomedConcept("% aggregation (qualifier value)"),
            DummySnomedConcept("Klinefelter's syndrome XXXY (disorder)"),
            DummySnomedConcept("XXXXY syndrome (disorder)"),
        ]


class DummyRedaction(object):
    def __init__(self):
        self.instruction = DummyInstruction()


def get_patient_record():
    practice = DummyPractice('MediData', '1234', '29390')
    patient_number = '2820'
    raw_xml = services.GetMedicalRecord(practice, patient_number).call()
    # redacted = redaction_elements(raw_xml, [".//Event[GUID='{12904CD5-1B75-4BBF-95ED-338EC0C6A5CC}']",
    #     ".//ConsultationElement[Attachment/GUID='{6BC4493F-DB5F-4C74-B585-05B0C3AA53C9}']",
    #     ".//ConsultationElement[Referral/GUID='{1FA96ED4-14F8-4322-B6F5-E00262AE124D}']",
    #     ".//Medication[GUID='{5A786379-97B4-44FD-9726-E3C9C5E34E32}']",
    #     ".//Medication[GUID='{A18F2B49-8ECA-436A-98F8-5C26E4F495DC}']",
    #     ".//Medication[GUID='{A1C57DC5-CCC6-4CD2-871B-C8A07ADC7D06}']",
    #     ".//Event[GUID='{EC323C66-8698-4802-9731-6AC229B11D6D}']",
    #     ".//Event[GUID='{6F058DA7-420E-422A-9CE6-84F3CA9CA246}']"])
    return MedicalRecord(raw_xml)


def edit_report(request):
    medical_record = get_patient_record()
    redaction = DummyRedaction()

    return render(request, 'medicalreport/medicalreport_edit.html', {
        'medical_record': medical_record,
        'redaction': redaction
    })
