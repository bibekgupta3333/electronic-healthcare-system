from .models import AdditionalMedicationRecords, AdditionalAllergies, AmendmentsForRecord
from snomedct.models import SnomedConcept
from datetime import datetime
from .forms import MedicalReportFinaliseSubmitForm
from django.contrib import messages

UI_DATE_FORMAT = '%m/%d/%Y'


def create_or_update_redaction_record(request, instruction):
    try:
        redaction = AmendmentsForRecord.objects.get(instruction=instruction)
    except AmendmentsForRecord.DoesNotExist:
        redaction = AmendmentsForRecord()
    status = request.POST.get('event_flag')
    if request.method == "POST":
        submit_form = MedicalReportFinaliseSubmitForm(request.user, request.POST)
        if status == 'draft':
            redaction.status = AmendmentsForRecord.REDACTION_STATUS_DRAFT
        elif status == 'submit':
            redaction.status = AmendmentsForRecord.REDACTION_STATUS_SUBMIT
        else:
            redaction.status = AmendmentsForRecord.REDACTION_STATUS_NEW

        if submit_form.is_valid(post_data=request.POST):
            # TODO redirect to report page
            redaction.review_by = submit_form.cleaned_data['gp_practitioner']
            redaction.submit_choice = submit_form.cleaned_data['prepared_and_signed']
            redaction.prepared_by = submit_form.cleaned_data['prepared_by']
        else:
            messages.error(request, 'INVALID: Please Enter Reviewer')

    redaction.redacted_xpaths
    get_redation_xpaths(request, redaction)
    get_redaction_notes(request, redaction)
    get_additional_medication(request, redaction)
    get_additional_allergies(request, redaction)

    delete_additional_medication_records(request)
    delete_additional_allergies_records(request)

    redaction.instruction = instruction
    redaction.save()

    if status == 'draft':
        messages.success(request, 'Save medical report successful')


def get_redation_xpaths(request, redaction):
    redaction_xpaths = request.POST.getlist('redaction_xpaths')
    redaction.redacted_xpaths = redaction_xpaths


def get_redaction_notes(request, redaction):
    acute_notes = request.POST.get('redaction_acute_prescription_notes')
    repeat_notes = request.POST.get('redaction_repeat_prescription_notes')
    consultation_notes = request.POST.get('redaction_consultation_notes')
    referral_notes = request.POST.get('redaction_referral_notes')
    significant_problem_notes = request.POST.get('redaction_significant_problem_notes')
    bloods_notes = request.POST.get('redaction_bloods_notes')
    attachment_notes = request.POST.get('redaction_attachment_notes')

    redaction.acute_prescription_notes = acute_notes
    redaction.repeat_prescription_notes = repeat_notes
    redaction.consultation_notes = consultation_notes
    redaction.referral_notes = referral_notes
    redaction.significant_problem_notes = significant_problem_notes
    redaction.bloods_notes = bloods_notes
    redaction.attachment_notes = attachment_notes


def get_additional_allergies(request, redaction):
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

        record.redaction = redaction
        record.save()


def get_additional_medication(request, redaction):
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

        record.redaction = redaction
        record.save()


def delete_additional_medication_records(request):
    additional_medication_records_delete = request.POST.getlist('additional_medication_records_delete')
    if additional_medication_records_delete:
        AdditionalMedicationRecords.objects.filter(id__in=additional_medication_records_delete).delete()


def delete_additional_allergies_records(request):
    additional_allergies_records_delete = request.POST.getlist('additional_allergies_records_delete')
    if additional_allergies_records_delete:
        AdditionalAllergies.objects.filter(id__in=additional_allergies_records_delete).delete()
