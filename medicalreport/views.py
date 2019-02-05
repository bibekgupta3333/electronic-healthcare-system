from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from services.emisapiservices import services
from services.xml.medical_report_decorator import MedicalReportDecorator
from services.xml.medical_record import MedicalRecord
from .models import AmendmentsForRecord, ReferencePhrases
from services.xml.patient_list import PatientList
from services.xml.registration import Registration
from medicalreport.forms import MedicalReportFinaliseSubmitForm
from medicalreport.reports import AttachmentReport
from instructions.models import Instruction, InstructionPatient
from instructions.model_choices import INSTRUCTION_REJECT_TYPE, AMRA_TYPE, INSTRUCTION_STATUS_REJECT,\
    INSTRUCTION_STATUS_COMPLETE
from .functions import create_or_update_redaction_record, create_patient_report
from medicalreport.reports import MedicalReport
from accounts.models import GENERAL_PRACTICE_USER
from accounts.functions import create_or_update_patient_user
from organisations.models import OrganisationGeneralPractice
from .forms import AllocateInstructionForm
from permissions.functions import check_permission, check_user_type
from payment.functions import calculate_instruction_fee
from typing import List


@login_required(login_url='/accounts/login')
def view_attachment(request, instruction_id, path_file):
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    raw_xml_or_status_code = services.GetAttachment(instruction.patient.emis_number, path_file, gp_organisation=instruction.gp_practice).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    attachment_report = AttachmentReport(raw_xml_or_status_code)
    return attachment_report.render()


def get_matched_patient(patient: InstructionPatient, gp_organisation: OrganisationGeneralPractice) -> List[Registration]:
    raw_xml_or_status_code = services.GetPatientList(patient, gp_organisation=gp_organisation).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    patients = PatientList(raw_xml_or_status_code).patients()
    return patients


def get_patient_registration(patient_number, gp_organisation: OrganisationGeneralPractice):
    raw_xml_or_status_code = services.GetMedicalRecord(patient_number, gp_organisation=gp_organisation).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    patient_registration = MedicalRecord(raw_xml_or_status_code).registration()
    return patient_registration


@login_required(login_url='/accounts/login')
@check_user_type(GENERAL_PRACTICE_USER)
def reject_request(request, instruction_id):
    instruction = Instruction.objects.get(id=instruction_id)
    instruction.reject(request, request.POST)
    return HttpResponseRedirect("%s?%s"%(reverse('instructions:view_pipeline'),"status=%s&type=allType"%INSTRUCTION_STATUS_REJECT))


@login_required(login_url='/accounts/login')
@check_user_type(GENERAL_PRACTICE_USER)
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
                if request.user.id == instruction.gp_user.user.id:
                    patient_user = create_or_update_patient_user(instruction.patient_information, patient_emis_number)
                    instruction.patient = patient_user
                    instruction.save()
                else:
                    messages.success(request, 'Allocated to {gp_name} successful'.format(gp_name=gp_name))
                    return redirect('instructions:view_pipeline')
            elif allocate_option == AllocateInstructionForm.RETURN_TO_PIPELINE:
                return redirect('instructions:view_pipeline')
    if not AmendmentsForRecord.objects.filter(instruction=instruction).exists():
        AmendmentsForRecord.objects.create(instruction=instruction)
    instruction.in_progress(context={'gp_user': request.user.userprofilebase.generalpracticeuser})
    instruction.saved = False
    instruction.save()
    return redirect('medicalreport:edit_report', instruction_id=instruction_id)


@login_required(login_url='/accounts/login')
@check_permission
@check_user_type(GENERAL_PRACTICE_USER)
def set_patient_emis_number(request, instruction_id):
    instruction = Instruction.objects.get(id=instruction_id)
    patient_list = get_matched_patient(instruction.patient_information, gp_organisation=instruction.gp_practice)
    if isinstance(patient_list, HttpResponseRedirect):
        return patient_list
    allocate_instruction_form = AllocateInstructionForm(user=request.user, instruction_id=instruction_id)

    return render(request, 'medicalreport/patient_emis_number.html', {
        'patient_list': patient_list,
        'reject_types': INSTRUCTION_REJECT_TYPE,
        'instruction': instruction,
        'amra_type': AMRA_TYPE,
        'allocate_instruction_form': allocate_instruction_form
    })


@login_required(login_url='/accounts/login')
@check_permission
@check_user_type(GENERAL_PRACTICE_USER)
def edit_report(request, instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)

    try:
        redaction = AmendmentsForRecord.objects.get(instruction=instruction_id)
    except AmendmentsForRecord.DoesNotExist:
        return redirect('medicalreport:set_patient_emis_number', instruction_id=instruction_id)

    raw_xml_or_status_code = services.GetMedicalRecord(redaction.patient_emis_number, gp_organisation=instruction.gp_practice).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    medical_record_decorator = MedicalReportDecorator(raw_xml_or_status_code, instruction)
    questions = instruction.addition_questions.all()
    initial_prepared_by = request.user.userprofilebase.generalpracticeuser.pk
    if redaction.prepared_by:
        initial_prepared_by = redaction.prepared_by.pk
    finalise_submit_form = MedicalReportFinaliseSubmitForm(
        initial={
            'record_type': redaction.instruction.type,
            'SUBMIT_OPTION_CHOICES': (
                    ('PREPARED_AND_REVIEWED', format_html(
                        'Signed off by <span id="preparer"></span>'.format(request.user.first_name)),
                     ),
                ),
            'prepared_by': initial_prepared_by,
            'prepared_and_signed': redaction.submit_choice or AmendmentsForRecord.PREPARED_AND_REVIEWED,
            'instruction_checked': redaction.instruction_checked
        },
        user=request.user)

    relations = "|".join(relation.name for relation in ReferencePhrases.objects.all())
    inst_gp_user = instruction.gp_user.user
    cur_user = request.user
    return render(request, 'medicalreport/medicalreport_edit.html', {
        'user': request.user,
        'medical_record': medical_record_decorator,
        'redaction': redaction,
        'instruction': instruction,
        'finalise_submit_form': finalise_submit_form,
        'questions': questions,
        'relations': relations,
        'show_alert': True if inst_gp_user == cur_user else False
    })


@login_required(login_url='/accounts/login')
@check_user_type(GENERAL_PRACTICE_USER)
def update_report(request, instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)

    if request.is_ajax():
        create_or_update_redaction_record(request, instruction)
        return JsonResponse({'message': 'Report has been saved.'})
    else:
        if instruction.is_amra() and not instruction.consent_form:
            messages.error(request, "You do not have a consent form")
        elif instruction.is_sars() and not instruction.mdx_consent:
            messages.error(request, "You do not have a mdx consent")
        else:
            is_valid = create_or_update_redaction_record(request, instruction)
            if is_valid:
                if request.POST.get('event_flag') == 'submit':
                    if instruction.client_user:
                        calculate_instruction_fee(instruction)
                    create_patient_report(request, instruction)
                if request.POST.get('event_flag') == 'preview':
                    return redirect('medicalreport:submit_report', instruction_id=instruction_id)
                return redirect('instructions:view_pipeline')

        return redirect('medicalreport:edit_report', instruction_id=instruction_id)


@login_required(login_url='/accounts/login')
def submit_report(request, instruction_id):
    header_title = "Preview and Submit Report"
    instruction = get_object_or_404(Instruction, id=instruction_id)
    redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)

    patient_emis_number = instruction.patient.emis_number
    raw_xml_or_status_code = services.GetMedicalRecord(patient_emis_number, instruction.gp_practice).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    medical_record_decorator = MedicalReportDecorator(raw_xml_or_status_code, instruction)
    attachments = medical_record_decorator.attachments
    relations = "|".join(relation.name for relation in ReferencePhrases.objects.all())
    initial_prepared_by = request.user.userprofilebase.generalpracticeuser.pk
    if redaction.prepared_by:
        initial_prepared_by = redaction.prepared_by.pk
    finalise_submit_form = MedicalReportFinaliseSubmitForm(
        initial={
            'record_type': redaction.instruction.type,
            'SUBMIT_OPTION_CHOICES': (
                ('PREPARED_AND_REVIEWED', format_html(
                    'Signed off by <span id="preparer"></span>'.format(request.user.first_name)),
                 ),
            ),
            'prepared_by': initial_prepared_by,
            'prepared_and_signed': redaction.submit_choice or AmendmentsForRecord.PREPARED_AND_REVIEWED,
            'instruction_checked': redaction.instruction_checked
        },
        user=request.user)

    return render(request, 'medicalreport/medicalreport_submit.html', {
        'header_title': header_title,
        'attachments': attachments,
        'redaction': redaction,
        'relations': relations,
        'instruction': instruction,
        'finalise_submit_form': finalise_submit_form
    })


@login_required(login_url='/accounts/login')
def view_report(request, instruction_id):
    instruction = get_object_or_404(Instruction, id=instruction_id)
    if instruction.status != INSTRUCTION_STATUS_COMPLETE:
        redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)
        raw_xml_or_status_code = services.GetMedicalRecord(redaction.patient_emis_number, instruction.gp_practice).call()
        if isinstance(raw_xml_or_status_code, int):
            return redirect('services:handle_error', code=raw_xml_or_status_code)
        medical_record_decorator = MedicalReportDecorator(raw_xml_or_status_code, instruction)
        surgery_name = instruction.gp_practice
        relations = "|".join(relation.name for relation in ReferencePhrases.objects.all())

        params = {
            'medical_record': medical_record_decorator,
            'redaction': redaction,
            'instruction': instruction,
            'relations': relations,
            'surgery_name': surgery_name,
        }

        return MedicalReport.render(params)
    else:
        return HttpResponse(instruction.medical_report, content_type='application/pdf')


@login_required(login_url='/accounts/login')
@check_permission
def final_report(request, instruction_id):
    header_title = "Final Report"
    instruction = get_object_or_404(Instruction, id=instruction_id)
    redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)

    patient_emis_number = instruction.patient.emis_number
    raw_xml_or_status_code = services.GetMedicalRecord(patient_emis_number, instruction.gp_practice).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    medical_record_decorator = MedicalReportDecorator(raw_xml_or_status_code, instruction)
    attachments = medical_record_decorator.attachments
    relations = "|".join(relation.name for relation in ReferencePhrases.objects.all())

    return render(request, 'medicalreport/final_report.html', {
        'header_title': header_title,
        'attachments': attachments,
        'redaction': redaction,
        'relations': relations,
        'instruction': instruction
    })
