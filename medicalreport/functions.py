from .models import AdditionalMedicationRecords, AdditionalAllergies, Redaction
from snomedct.models import SnomedConcept


def create_redaction_record(request):
    redaction = Redaction()


def get_redation_xpaths(request):
    redaction_xpaths = request.POST.getlist('redaction_xpaths')


def get_redaction_notes(request):
    acute_notes = request.POST.get('redaction_acute_prescription_notes')
    repeat_notes = request.POST.get('redaction_repeat_prescription_notes')
    consultation_notes = request.POST.get('redaction_consultation_notes')
    referral_notes = request.POST.get('redaction_referral_notes')
    significant_problem_notes = request.POST.get('redaction_significant_problem_notes')
    bloods_notes = request.POST.get('redaction_bloods_notes')
    attachment_notes = request.POST.get('redaction_attachment_notes')

    return redaction_xpaths


def get_additional_allergies(request):
    additional_allergies_allergen = request.POST.get('additional_allergies_allergen')
    additional_allergies_reaction = request.POST.get('additional_allergies_reaction')
    additional_allergies_date_discovered = request.POST.get('additional_allergies_date_discovered')
    if additional_allergies_allergen is not None and
        additional_allergies_reaction is not None:
        record = AdditionalAllergies()
        record.allergen = additional_allergies_allergen
        record.reaction = additional_allergies_reaction
        record.date_discovered = additional_allergies_date_discovered


def get_additional_medication(request):
    additional_medication_type = request.POST.get('additional_medication_records_type')
    additional_medication_snomedct = request.POST.get('additional_medication_related_condition')
    additional_medication_drug = request.POST.get('additional_medication_drug')
    additional_medication_dose = request.POST.get('additional_medication_dose')
    additional_medication_frequency = request.POST.get('additional_medication_frequency')
    additional_medication_prescribed_from = request.POST.get('additional_medication_prescribed_from')
    additional_medication_prescribed_to = request.POST.get('additional_medication_prescribed_to')
    additional_medication_notes = request.POST.get('additional_medication_notes')

    if (additional_medication_type is not None and additional_medication_drug is not None and
            additional_medication_snomedct is not None and additional_medication_dose is not None and
            additional_medication_frequency is not None):
            record = AdditionalMedicationRecords()
            if additional_medication_type == "acute":
                record.repeat = False
            else:
                record.repeat = True

            record.snomed_concept = SnomedConcept.objects.get(id=additional_medication_snomedct)
            record.dose = additional_medication_dose
            record.drug = additional_medication_drug
            record.frequency = additional_medication_frequency
            record.notes = additional_medication_notes
            record.prescribed_from = additional_medication_prescribed_from
            record.prescribed_to = additional_medication_prescribed_to

            

