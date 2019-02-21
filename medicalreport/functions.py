import uuid
import logging
from datetime import datetime

from django.contrib import messages
from django.core.mail import send_mail
from django.template import loader
from django.utils.html import format_html
from django.shortcuts import redirect
from django.utils import timezone
from django.core.files.base import ContentFile
from services.xml.medical_report_decorator import MedicalReportDecorator
from snomedct.models import SnomedConcept
from services.emisapiservices import services
from services.xml.xml_utils import redaction_elements, lxml_to_string
from instructions import models
from .forms import MedicalReportFinaliseSubmitForm
from .models import AdditionalMedicationRecords, AdditionalAllergies, AmendmentsForRecord,\
        ReferencePhrases
from medicalreport.reports import MedicalReport
from report.models import PatientReportAuth
from report.tasks import generate_medicalreport_with_attachment


UI_DATE_FORMAT = '%m/%d/%Y'
logger = logging.getLogger('timestamp')


def create_or_update_redaction_record(request, instruction):
    try:
        amendments_for_record = AmendmentsForRecord.objects.get(instruction=instruction)
    except AmendmentsForRecord.DoesNotExist:
        amendments_for_record = AmendmentsForRecord()
    status = request.POST.get('event_flag')

    if status != 'submit':
        get_redaction_xpaths(request, amendments_for_record)
        get_redaction_notes(request, amendments_for_record)
        get_redaction_conditions(request, amendments_for_record)
        success = get_additional_medication(request, amendments_for_record) or get_additional_allergies(request, amendments_for_record)

        delete_additional_medication_records(request)
        delete_additional_allergies_records(request)

        amendments_for_record.instruction = instruction
        questions = instruction.addition_questions.all()
        for question in questions:
            input_answer = request.POST.get('answer-question-{question_id}'.format(question_id=question.id))
            answer_obj = models.InstructionAdditionAnswer.objects.filter(question=question).first()
            if answer_obj:
                answer_obj.answer = input_answer
                answer_obj.save()
            else:
                models.InstructionAdditionAnswer.objects.create(question=question, answer=input_answer)

    if status == 'add-medication':
        if success:
            messages.success(request, 'Add Medication Successfully')
        else:
            messages.error(request, 'Missing Medication required field')
    elif status == 'add-allergies':
        if success:
            messages.success(request, 'Add Allergies Successfully')
        else:
            messages.error(request, 'Missing Allergies required field')

    if request.method == "POST":
        submit_form = MedicalReportFinaliseSubmitForm(request.user, request.POST,
                                                      initial={
                                                          'record_type': instruction.type,
                                                          'SUBMIT_OPTION_CHOICES': (
                                                              ('PREPARED_AND_SIGNED',
                                                               'Prepared and signed directly by {}'.format(
                                                                   request.user.first_name)),
                                                              ('PREPARED_AND_REVIEWED', format_html(
                                                                        'Signed off by <span id="preparer"></span>'
                                                                    ),
                                                               ),

                                                          ),
                                                      'instruction_checked': amendments_for_record.instruction_checked
                                                      },
                                                      )
        if status in ['draft', 'preview']:
            amendments_for_record.status = AmendmentsForRecord.REDACTION_STATUS_DRAFT
        elif status == 'submit':
            amendments_for_record.status = AmendmentsForRecord.REDACTION_STATUS_SUBMIT
        else:
            amendments_for_record.status = AmendmentsForRecord.REDACTION_STATUS_NEW

        if submit_form.is_valid(post_data=request.POST):
            if not status:
                amendments_for_record.instruction_checked = submit_form.cleaned_data['instruction_checked']
            amendments_for_record.submit_choice = submit_form.cleaned_data.get('prepared_and_signed')
            amendments_for_record.review_by = request.user
            if submit_form.cleaned_data.get('prepared_and_signed') == AmendmentsForRecord.PREPARED_AND_SIGNED:
                amendments_for_record.prepared_by = request.user.userprofilebase.generalpracticeuser
            else:
                amendments_for_record.prepared_by = submit_form.cleaned_data.get('prepared_by')

            if status == 'submit':
                instruction.status = models.INSTRUCTION_STATUS_COMPLETE
                instruction.completed_signed_off_timestamp = timezone.now()
                messages.success(request, 'Completed Medical Report')

            instruction.save()
            amendments_for_record.save()
            if status == 'submit':
                save_medical_report(request, instruction, amendments_for_record)
            elif status and status not in ['submit', 'draft', 'preview']:
                return False

            return True
        else:
            if status not in ['add-medication', 'add-allergies']:
                messages.error(request, submit_form._errors)
            return False

    amendments_for_record.save()

    if status == 'draft':
        messages.success(request, 'Save Medical Report Successful')

    return True


def save_medical_report(request, instruction, amendments_for_record):
    start_time = timezone.now()
    raw_xml_or_status_code = services.GetMedicalRecord(amendments_for_record.patient_emis_number, gp_organisation=instruction.gp_practice).call()
    if isinstance(raw_xml_or_status_code, int):
        return redirect('services:handle_error', code=raw_xml_or_status_code)
    medical_record_decorator = MedicalReportDecorator(raw_xml_or_status_code, instruction)
    relations = '|'.join(relation.name for relation in ReferencePhrases.objects.all())
    parse_xml = redaction_elements(raw_xml_or_status_code, amendments_for_record.redacted_xpaths)
    str_xml = lxml_to_string(parse_xml)
    params = {
        'medical_record': medical_record_decorator,
        'relations': relations,
        'redaction': amendments_for_record,
        'instruction': instruction,
        'surgery_name': instruction.gp_practice,
    }
    uuid_hex = uuid.uuid4().hex
    instruction.medical_report.save('report_%s.pdf'%uuid_hex, MedicalReport.get_pdf_file(params))
    instruction.medical_xml_report.save('xml_report_%s.xml'%uuid_hex, ContentFile(str_xml))
    end_time = timezone.now()
    total_time = end_time - start_time
    logger.info("[SAVING PDF AND XML] %s seconds with patient %s"%(total_time.seconds, instruction.patient_information.__str__()))


def get_redaction_xpaths(request, amendments_for_record):
    redaction_xpaths = request.POST.getlist('redaction_xpaths')
    amendments_for_record.redacted_xpaths = redaction_xpaths


def get_redaction_conditions(request, amendments_for_record):

    redaction_conditions = set(filter(None, request.POST.getlist('map_code')))
    if 'undefined'in redaction_conditions: redaction_conditions.remove('undefined')
    amendments_for_record.re_redacted_codes = list(redaction_conditions)


def get_redaction_notes(request, amendments_for_record):
    acute_notes = request.POST.get('redaction_acute_prescription_notes', '')
    repeat_notes = request.POST.get('redaction_repeat_prescription_notes', '')
    consultation_notes = request.POST.get('redaction_consultation_notes', '')
    referral_notes = request.POST.get('redaction_referral_notes', '')
    significant_problem_notes = request.POST.get('redaction_significant_problem_notes', '')
    bloods_notes = request.POST.get('redaction_bloods_notes', '')
    attachment_notes = request.POST.get('redaction_attachment_notes', '')
    comment_notes = request.POST.get('redaction_comment_notes', '')

    amendments_for_record.acute_prescription_notes = acute_notes
    amendments_for_record.repeat_prescription_notes = repeat_notes
    amendments_for_record.consultation_notes = consultation_notes
    amendments_for_record.referral_notes = referral_notes
    amendments_for_record.significant_problem_notes = significant_problem_notes
    amendments_for_record.bloods_notes = bloods_notes
    amendments_for_record.attachment_notes = attachment_notes
    amendments_for_record.comment_notes = comment_notes


def get_additional_allergies(request, amendments_for_record):
    additional_allergies_allergen = request.POST.get('additional_allergies_allergen')
    additional_allergies_reaction = request.POST.get('additional_allergies_reaction')
    additional_allergies_date_discovered = request.POST.get('additional_allergies_date_discovered')

    if (additional_allergies_allergen and
            additional_allergies_reaction):
        record = AdditionalAllergies()
        record.allergen = additional_allergies_allergen
        record.reaction = additional_allergies_reaction
        if additional_allergies_date_discovered:
            record.date_discovered = datetime.strptime(additional_allergies_date_discovered, UI_DATE_FORMAT)

        record.amendments_for_record = amendments_for_record
        record.save()
        return True
    else:
        return False


def get_additional_medication(request, amendments_for_record):
    additional_medication_type = request.POST.get('additional_medication_records_type')
    additional_medication_snomedct = request.POST.get('additional_medication_related_condition')
    additional_medication_drug = request.POST.get('additional_medication_drug')
    additional_medication_dose = request.POST.get('additional_medication_dose')
    additional_medication_frequency = request.POST.get('additional_medication_frequency')
    additional_medication_prescribed_from = request.POST.get('additional_medication_prescribed_from')
    additional_medication_prescribed_to = request.POST.get('additional_medication_prescribed_to')
    additional_medication_notes = request.POST.get('additional_medication_notes')

    if (additional_medication_type and additional_medication_drug
            and additional_medication_dose and additional_medication_frequency):
        record = AdditionalMedicationRecords()
        if additional_medication_type == "acute":
            record.repeat = False
        else:
            record.repeat = True

        if additional_medication_snomedct:
            try:
                record.snomed_concept = SnomedConcept.objects.get(pk=additional_medication_snomedct)
            except SnomedConcept.DoesNotExist:
                pass
        record.dose = additional_medication_dose
        record.drug = additional_medication_drug
        record.frequency = additional_medication_frequency
        record.notes = additional_medication_notes

        if additional_medication_prescribed_from:
            record.prescribed_from = datetime.strptime(additional_medication_prescribed_from, UI_DATE_FORMAT)

        if additional_medication_prescribed_to:
            record.prescribed_to = datetime.strptime(additional_medication_prescribed_to, UI_DATE_FORMAT)

        record.amendments_for_record = amendments_for_record
        record.save()
        return True
    else:
        return False


def delete_additional_medication_records(request):
    additional_medication_records_delete = request.POST.getlist('additional_medication_records_delete')
    if additional_medication_records_delete:
        AdditionalMedicationRecords.objects.filter(id__in=additional_medication_records_delete).delete()


def delete_additional_allergies_records(request):
    additional_allergies_records_delete = request.POST.getlist('additional_allergies_records_delete')
    if additional_allergies_records_delete:
        AdditionalAllergies.objects.filter(id__in=additional_allergies_records_delete).delete()


def send_surgery_email(instruction):
    send_mail(
        'Medidata eMR: Your medical report is ready',
        'Your instruction has been submitted',
        'MediData',
        [instruction.gp_practice.organisation_email],
        fail_silently=True,
        html_message=loader.render_to_string('medicalreport/surgery_email.html',
                                             {
                                                 'name': instruction.patient.user.first_name,
                                                 'gp': instruction.gp_user.user.first_name,
                                             }
                                             ))


def create_patient_report(request, instruction):
    unique_url = uuid.uuid4().hex
    PatientReportAuth.objects.create(patient=instruction.patient, instruction=instruction, url=unique_url)
    report_link_info = {
        'scheme': request.scheme,
        'host': request.get_host(),
        'unique_url': unique_url
    }
    generate_medicalreport_with_attachment.delay(instruction.id, report_link_info)
    send_surgery_email(instruction)


