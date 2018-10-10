from .models import AdditionalMedicationRecords, AdditionalAllergies, AmendmentsForRecord
from snomedct.models import SnomedConcept
from datetime import datetime
from .forms import MedicalReportFinaliseSubmitForm
from django.contrib import messages
from instructions import models

UI_DATE_FORMAT = '%m/%d/%Y'


def create_or_update_redaction_record(request, instruction):
    try:
        amendments_for_record = AmendmentsForRecord.objects.get(instruction=instruction)
    except AmendmentsForRecord.DoesNotExist:
        amendments_for_record = AmendmentsForRecord()
    status = request.POST.get('event_flag')

    get_redation_xpaths(request, amendments_for_record)
    get_redaction_notes(request, amendments_for_record)
    get_additional_medication(request, amendments_for_record)
    get_additional_allergies(request, amendments_for_record)

    delete_additional_medication_records(request)
    delete_additional_allergies_records(request)

    amendments_for_record.instruction = instruction

    if request.method == "POST":
        submit_form = MedicalReportFinaliseSubmitForm(request.user, request.POST)
        if status == 'draft':
            amendments_for_record.status = AmendmentsForRecord.REDACTION_STATUS_DRAFT
        elif status == 'submit':
            amendments_for_record.status = AmendmentsForRecord.REDACTION_STATUS_SUBMIT
        else:
            amendments_for_record.status = AmendmentsForRecord.REDACTION_STATUS_NEW

        if submit_form.is_valid(post_data=request.POST):
            # TODO redirect to report page
            amendments_for_record.review_by = submit_form.cleaned_data['gp_practitioner']
            amendments_for_record.submit_choice = submit_form.cleaned_data['prepared_and_signed']
            amendments_for_record.prepared_by = submit_form.cleaned_data['prepared_by']
            instruction.status = models.INSTRUCTION_STATUS_COMPLETE
            instruction.save()
            amendments_for_record.save()
            messages.success(request, 'Completed Medical Report')
            return True
        else:
            messages.error(request, submit_form._errors)
            return False

    amendments_for_record.save()

    if status == 'draft':
        messages.success(request, 'Save Medical Report Successful')

    return True


def get_redation_xpaths(request, amendments_for_record):
    redaction_xpaths = request.POST.getlist('redaction_xpaths')
    amendments_for_record.redacted_xpaths = redaction_xpaths


def get_redaction_notes(request, amendments_for_record):
    acute_notes = request.POST.get('redaction_acute_prescription_notes')
    repeat_notes = request.POST.get('redaction_repeat_prescription_notes')
    consultation_notes = request.POST.get('redaction_consultation_notes')
    referral_notes = request.POST.get('redaction_referral_notes')
    significant_problem_notes = request.POST.get('redaction_significant_problem_notes')
    bloods_notes = request.POST.get('redaction_bloods_notes')
    attachment_notes = request.POST.get('redaction_attachment_notes')
    comment_notes = request.POST.get('redaction_comment_notes')

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


def get_additional_medication(request, amendments_for_record):
    additional_medication_type = request.POST.get('additional_medication_records_type')
    additional_medication_snomedct = request.POST.get('additional_medication_related_condition')
    additional_medication_drug = request.POST.get('additional_medication_drug')
    additional_medication_dose = request.POST.get('additional_medication_dose')
    additional_medication_frequency = request.POST.get('additional_medication_frequency')
    additional_medication_prescribed_from = request.POST.get('additional_medication_prescribed_from')
    additional_medication_prescribed_to = request.POST.get('additional_medication_prescribed_to')
    additional_medication_notes = request.POST.get('additional_medication_notes')

    if (additional_medication_type and additional_medication_drug and additional_medication_snomedct
            and additional_medication_dose and additional_medication_frequency):
        record = AdditionalMedicationRecords()
        if additional_medication_type == "acute":
            record.repeat = False
        else:
            record.repeat = True

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


def delete_additional_medication_records(request):
    additional_medication_records_delete = request.POST.getlist('additional_medication_records_delete')
    if additional_medication_records_delete:
        AdditionalMedicationRecords.objects.filter(id__in=additional_medication_records_delete).delete()


def delete_additional_allergies_records(request):
    additional_allergies_records_delete = request.POST.getlist('additional_allergies_records_delete')
    if additional_allergies_records_delete:
        AdditionalAllergies.objects.filter(id__in=additional_allergies_records_delete).delete()
