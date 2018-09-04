from django.shortcuts import render, redirect
from django.http import HttpResponse
from services.dummy_models import DummyPractice
from services.emisapiservices import services
from services.xml.medical_report_decorator import MedicalReportDecorator

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
        self.redacted_xpaths = [
            ".//ConsultationElement[Referral/GUID='{1FA96ED4-14F8-4322-B6F5-E00262AE124D}']",
            ".//ConsultationElement[Attachment/GUID='{6BC4493F-DB5F-4C74-B585-05B0C3AA53C9}']",
            ".//Consultation[GUID='{94DAFC52-26F4-4341-BFDB-397FA67C17E2}']",
            ".//Event[GUID='{13021918-0B2B-44E7-AC28-A6643D4CFEC9}']",
            ".//Medication[GUID='{A85327B8-3106-480A-BDD3-0777D0F267D1}']"
        ]

    def redacted(self, xpaths):
        return all(xpath in self.redacted_xpaths for xpath in xpaths)


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

    medical_record_decorator = MedicalReportDecorator(raw_xml, None)
    return medical_record_decorator


def edit_report(request):
    medical_record = get_patient_record()
    redaction = DummyRedaction()

    return render(request, 'medicalreport/medicalreport_edit.html', {
        'medical_record': medical_record,
        'redaction': redaction
    })


def update_report(request):
    print("POST data=", request.POST)
    print("redaction_patch_xpaths=", request.POST.getlist('redaction_patch_xpaths'))
    return redirect('medicalreport:edit')
    # return HttpResponse("ok")
