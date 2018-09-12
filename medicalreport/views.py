from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse
from services.dummy_models import DummyPractice
from services.emisapiservices import services
from services.xml.medical_report_decorator import MedicalReportDecorator
from .dummy_models import (DummyInstruction, DummyClient)
from .models import Redaction
from instructions.models import Instruction
from .functions import create_or_update_redaction_record


# Create your views here.
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


def edit_report(request, instruction_id):
    medical_record = get_patient_record()
    try:
        redaction = Redaction.objects.get(instruction=instruction_id)
    except Redaction.DoesNotExist:
        redaction = Redaction()

    instruction = Instruction.objects.get(id=instruction_id)
    dummy_client = DummyClient(instruction.client_user.organisation)
    dummy_instruction = DummyInstruction(instruction.id, dummy_client)

    return render(request, 'medicalreport/medicalreport_edit.html', {
        'medical_record': medical_record,
        'redaction': redaction,
        'instruction': dummy_instruction
    })


def update_report(request, instruction_id):
    print("POST data=", request.POST)
    print("instruction id: ", instruction_id)

    instruction = get_object_or_404(Instruction, id=instruction_id)
    create_or_update_redaction_record(request, instruction)
    return redirect('medicalreport:edit_report', instruction_id=instruction_id)
