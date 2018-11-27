from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from services.emisapiservices import services
from services.xml.medical_report_decorator import MedicalReportDecorator
from services.xml.patient_list import PatientList
from services.xml.registration import Registration
from .dummy_models import (DummyInstruction)
from medicalreport.forms import MedicalReportFinaliseSubmitForm
from .models import AmendmentsForRecord
from medicalreport.reports import AttachmentReport
from instructions.models import Instruction, InstructionPatient
from instructions.model_choices import INSTRUCTION_REJECT_TYPE, AMRA_TYPE, INSTRUCTION_STATUS_REJECT
from .functions import create_or_update_redaction_record, create_patient_report
from medicalreport.reports import MedicalReport
from accounts.models import GeneralPracticeUser, User
from accounts.functions import create_or_update_patient_user
from .forms import AllocateInstructionForm
from permissions.functions import check_permission
from typing import List


@login_required(login_url='/accounts/login')
def view_attachment(request, instruction_id, path_file):
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    attachment_report = AttachmentReport(instruction, path_file)
    return attachment_report.render()


def get_matched_patient(patient: InstructionPatient) -> List[Registration]:
    raw_xml = services.GetPatientList(patient).call()
    patients = PatientList(raw_xml).patients()
    return patients


# JT - why is this function here? It isn't used anywhere.
def get_patient_record(patient_number):
    raw_xml = services.GetMedicalRecord(patient_number).call()
    # redacted = redaction_elements(raw_xml, [".//Event[GUID='{12904CD5-1B75-4BBF-95ED-338EC0C6A5CC}']",
    #     ".//ConsultationElement[Attachment/GUID='{6BC4493F-DB5F-4C74-B585-05B0C3AA53C9}']",
    #     ".//ConsultationElement[Referral/GUID='{1FA96ED4-14F8-4322-B6F5-E00262AE124D}']",
    #     ".//Medication[GUID='{5A786379-97B4-44FD-9726-E3C9C5E34E32}']",
    #     ".//Medication[GUID='{A18F2B49-8ECA-436A-98F8-5C26E4F495DC}']",
    #     ".//Medication[GUID='{A1C57DC5-CCC6-4CD2-871B-C8A07ADC7D06}']",
    #     ".//Event[GUID='{EC323C66-8698-4802-9731-6AC229B11D6D}']",
    #     ".//Event[GUID='{6F058DA7-420E-422A-9CE6-84F3CA9CA246}']"])
    return raw_xml


@login_required(login_url='/accounts/login')
def reject_request(request, instruction_id):
    instruction = Instruction.objects.get(id=instruction_id)
    instruction.reject(request, request.POST)
    return HttpResponseRedirect("%s?%s"%(reverse('instructions:view_pipeline'),"status=%s&type=allType"%INSTRUCTION_STATUS_REJECT))


@login_required(login_url='/accounts/login')
def select_patient(request, instruction_id, patient_emis_number):
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    if request.method == 'POST':
        allocate_instruction_form = AllocateInstructionForm(request.user, instruction_id, request.POST)
        if allocate_instruction_form.is_valid():
            allocate_option = int(allocate_instruction_form.cleaned_data['allocate_options'])
            if allocate_option == AllocateInstructionForm.PROCEED_REPORT:
                patient_user = create_or_update_patient_user(instruction.patient_information, patient_emis_number)
                instruction.patient = patient_user
                instruction.gp_user = request.user.userprofilebase.generalpracticeuser
                instruction.save()
                messages.success(request, 'Allocated to self successful')
            elif allocate_option == AllocateInstructionForm.ALLOCATE:
                instruction.gp_user = allocate_instruction_form.cleaned_data['gp_practitioner'].userprofilebase.generalpracticeuser
                instruction.save()
                gp_name = ' '.join([instruction.gp_user.user.first_name, instruction.gp_user.user.last_name])
                messages.success(request, 'Allocated to {gp_name} successful'.format(gp_name=gp_name))
                return redirect('instructions:view_pipeline')
            elif allocate_option == AllocateInstructionForm.RETURN_TO_PIPELINE:
                return redirect('instructions:view_pipeline')
    if not AmendmentsForRecord.objects.filter(instruction=instruction).exists():
        AmendmentsForRecord.objects.create(instruction=instruction)
    gp_user = get_object_or_404(GeneralPracticeUser, user_id=request.user.id)
    instruction.in_progress(context={'gp_user': gp_user})
    instruction.saved = False
    instruction.save()
    return redirect('medicalreport:edit_report', instruction_id=instruction_id)


@login_required(login_url='/accounts/login')
@check_permission
def set_patient_emis_number(request, instruction_id):
    instruction = Instruction.objects.get(id=instruction_id)
    dummy_instruction = DummyInstruction(instruction)
    patient_list = get_matched_patient(instruction.patient_information)
    allocate_instruction_form = AllocateInstructionForm(user=request.user, instruction_id=instruction_id)

    return render(request, 'medicalreport/patient_emis_number.html', {
        'patient_list': patient_list,
        'reject_types': INSTRUCTION_REJECT_TYPE,
        'instruction': instruction,
        'amra_type': AMRA_TYPE,
        'dummy_instruction': dummy_instruction,
        'allocate_instruction_form': allocate_instruction_form
    })


@login_required(login_url='/accounts/login')
@check_permission
def edit_report(request, instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)
    try:
        redaction = AmendmentsForRecord.objects.get(instruction=instruction_id)
    except AmendmentsForRecord.DoesNotExist:
        return redirect('medicalreport:set_patient_emis_number', instruction_id=instruction_id)

    raw_xml = services.GetMedicalRecord(redaction.patient_emis_number).call()
    # print('\n', raw_xml, '\n')
    medical_record_decorator = MedicalReportDecorator(raw_xml, instruction)
    questions = instruction.addition_questions.all()
    finalise_submit_form = MedicalReportFinaliseSubmitForm(
        initial={
            'record_type': redaction.instruction.type,
            'SUBMIT_OPTION_CHOICES': (
                    ('PREPARED_AND_SIGNED', 'Prepared and signed directly by {}'.format(request.user.first_name)),
                    ('PREPARED_AND_REVIEWED', format_html('Prepared by <span id="preparer"></span> and reviewed by {}'
                                                          .format(request.user.first_name)),
                     )

                ),
            'prepared_by': redaction.prepared_by,
            'prepared_and_signed': redaction.submit_choice,
            'instruction_checked': redaction.instruction_checked
        },
        user=request.user)

    inst_gp_user = User.objects.get(username=instruction.gp_user.user.username)
    cur_user = User.objects.get(username=request.user.username)
    return render(request, 'medicalreport/medicalreport_edit.html', {
        'user': request.user,
        'medical_record': medical_record_decorator,
        'redaction': redaction,
        'instruction': instruction,
        'finalise_submit_form': finalise_submit_form,
        'questions': questions,
        'show_alert': True if inst_gp_user == cur_user else False
    })


@login_required(login_url='/accounts/login')
def update_report(request, instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)

    if request.is_ajax():
        create_or_update_redaction_record(request, instruction)
        return JsonResponse({'message': 'Report has been saved.'})
    else:
        if not instruction.consent_form:
            messages.error(request, "You do not have a consent form")
        else:
            is_valid = create_or_update_redaction_record(request, instruction)
            if request.POST.get('event_flag') == 'submit' and is_valid:
                create_patient_report(instruction)
                return redirect('instructions:view_pipeline')

        return redirect('medicalreport:edit_report', instruction_id=instruction_id)


@login_required(login_url='/accounts/login')
def view_report(request, instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)
    redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)

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

    return MedicalReport.render(params)


@login_required(login_url='/accounts/login')
@check_permission
def final_report(request, instruction_id):
    header_title = "Final Report"
    instruction = get_object_or_404(Instruction, id=instruction_id)
    redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)

    patient_emis_number = instruction.patient.emis_number
    raw_xml = services.GetMedicalRecord(patient_emis_number).call()
    medical_record_decorator = MedicalReportDecorator(raw_xml, instruction)
    attachments = medical_record_decorator.attachments

    return render(request, 'medicalreport/final_report.html', {
        'header_title': header_title,
        'attachments': attachments,
        'redaction': redaction,
        'instruction': instruction
    })
