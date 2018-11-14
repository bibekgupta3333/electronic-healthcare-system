from django import template
from .helper import diagnosed_date, linked_problems, end_date, format_date, additional_medication_dates_description
import re
register = template.Library()


@register.filter
def instruction_patient_address(patient):
    address_lines = [patient.address_name_number, patient.address_line2,
                     patient.address_line3, patient.address_line4,
                     patient.address_postcode, patient.address_country]
    address_lines = list(filter(None, address_lines))
    return ", ".join(address_lines)


@register.filter
def patient_address(patient):
    address = patient.address_lines()
    return ", ".join(address)

@register.filter
def patient_description(patient):
    description = [patient.full_name(), format_date(patient.parsed_date_of_birth())] + patient.address_lines()
    description = list(filter(None, description))
    description = ", ".join(description)
    return description


@register.filter
def format_date_filter(date):
    return format_date(date)


@register.filter
def additional_medication_header(record):
    fsn_description = ''
    if record.snomed_concept is not None:
        fsn_description = record.snomed_concept.fsn_description
    return "{} prescribed for '{}'.".format(record.drug, fsn_description)


@register.filter
def additional_medication_body(record):
    return "{} {} {}. Additional contextual information:{}".format(
        record.dose, record.frequency, additional_medication_dates_description(record), record.notes
    )


@register.filter
def additional_allergy_description(record):
    prefix = ''
    if record.date_discovered:
        prefix = "{} - ".format(format_date(record.date_discovered))

    return "{}{}, {}".format(prefix, record.allergen, record.reaction)


@register.filter
def active_problem_header(problem, problem_list):
    return "{} {}".format(problem.description(), diagnosed_date(problem, linked_problems(problem, problem_list)))


@register.filter
def past_problem_header(problem):
    return "{} {}".format(problem.description(), end_date(problem))


@register.filter
def general_header(model):
    return "{} - {}".format(format_date(model.parsed_date()), model.description())


@register.filter
def referral_body(referral, locations):
    provider = None
    for location in locations:
        if location.ref_id() == referral.provider_refid():
            provider = location
            break
    if provider is not None:
        return ', '.join(provider.address_lines())
    return ''


@register.filter
def consultation_header(consultation, people):
    author = None
    for p in people:
        if p.ref_id() == consultation.original_author_refid():
            author = p
    if author is not None:
        return "{} - {}".format(format_date(consultation.parsed_date()), author.full_name())
    else:
        return format_date(consultation.parsed_date())


@register.filter
def consultaion_sick_note(consultation):
    if consultation.is_sick_note():
        return 'sick note'
    else:
        return None


@register.filter
def profile_event_value_header(key):
    header = {
        "height": "Height",
        "weight": "Weight",
        "bmi": "BMI",
        "smoking": "Smoking",
        "alcohol": "Alcohol",
        "systolic_blood_pressure": "Systolic Blood Pressure",
        "diastolic_blood_pressure": "Diastolic Blood Pressure",
        "spirometry": "Spirometry (FVC, FEV1)",
        "peak_flow": "Peak flow",
        "cervical_smear_test": "Cervical smear test",
        "illicit_drug_use": "Illicit drug use"
    }
    return header[key]


@register.filter
def event_value_body(event):
    # print(type(event))
    if event:
        return "{}<br>{}".format(format_date(event.parsed_date()), event.description())
    else:
        return "N/A"


@register.filter
def bloods_type_value_header(key):
    header = {
        "white_blood_count": "WBC",
        "hemoglobin": "Hb",
        "platelets": "Platelets",
        "mean_cell_volume": "MCV",
        "mean_corpuscular_hemoglobin": "MCH",
        "neutrophils": "Neutrophils",
        "lymphocytes": "Lymphocytes",
        "sodium": "Sodium",
        "potassium": "Potassium",
        "urea": "Urea",
        "creatinine": "Creatinine",
        "c_reactive_protein": "CRP",
        "bilirubin": "Bilirubin",
        "alkaline_phosphatase": "ALP",
        "alanine_aminotransferase": "ALT",
        "albumin": "Albumin",
        "gamma_gt": "Gamma-GT",
        "triglycerides": "Triglycerides",
        "total_cholesterol": "Total Cholesterol",
        "high_density_lipoprotein": "HDL",
        "low_density_lipoprotein": "LDL",
        "random_glucose": "Random Glucose",
        "fasting_glucose": "Fasting Glucose",
        "hba1c": "HbA1c",
    }
    return header[key]


@register.filter
def consultation_element_list(consultation):
    data = list()
    regex = re.compile(r"\.\s*\Z", re.IGNORECASE)
    for element in consultation.consultation_elements():
        header = element.header()
        obj = {}
        if header in obj:
            obj[header] = regex.sub('', obj[header]) + '. {}'.format(element.content().description())
        else:
            obj[header] = element.content().description()
        obj['xpath'] = element.xpaths()
        obj['map_code'] = element.map_code()
        data.append(obj)
    return data

@register.filter
def map_code(consultation):
    return consultation.map_code()


@register.filter
def hash(h, key):
    return h[key]