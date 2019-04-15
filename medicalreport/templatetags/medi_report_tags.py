from django import template
from django.db.models import Q
from .helper import problem_xpaths
from django.utils.html import format_html
from medicalreport.models import NhsSensitiveConditions

register = template.Library()


@register.inclusion_tag('medicalreport/inclusiontags/patient_info.html', takes_context=True)
def patient_info(context):
    return {
        'medical_record': context['medical_record'],
        'instruction': context['instruction']
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_referrals.html', takes_context=True)
def form_referrals(context):
    return {
        'referrals': context['medical_record'].referrals,
        'locations': context['medical_record'].locations,
        'instruction': context['instruction'],
        'minor_problems_list': context['medical_record'].minor_problems,
        'redaction': context['redaction'],
        'word_library': context['word_library'],
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_attachments.html', takes_context=True)
def form_attachments(context):
    return {
        'attachments': context['medical_record'].attachments,
        'instruction': context['instruction'],
        'redaction': context['redaction']
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_consultations.html', takes_context=True)
def form_consultations(context):
    return {
        'consultations': context['medical_record'].consultations,
        'relations': context['relations'],
        'people': context['medical_record'].people,
        'redaction': context['redaction'],
        'word_library': context['word_library'],
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_profile.html', takes_context=True)
def form_profile(context):
    return {
        'profile_events': context['medical_record'].profile_events_by_type,
        'profile_sex': context['medical_record'].registration().sex()
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_bloods.html', takes_context=True)
def form_bloods(context):
    return {
        'results': context['medical_record'].blood_test_results_by_type,
        'redaction': context['redaction'],
        'instruction_type': context['instruction'].type
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_significant_problems.html', takes_context=True)
def form_significant_problems(context):
    return {
        'significant_active_problems': context['medical_record'].significant_active_problems,
        'significant_past_problems': context['medical_record'].significant_past_problems,
        'problem_linked_lists': context['medical_record'].problem_linked_lists,
        'redaction': context['redaction'],
        'word_library': context['word_library'],
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_medications.html', takes_context=True)
def form_medications(context):
    return {
        'acute_medications': context['medical_record'].acute_medications,
        'repeat_medications': context['medical_record'].repeat_medications,
        'additional_acute_medications': context['redaction'].additional_acute_medications,
        'additional_repeat_medications': context['redaction'].additional_repeat_medications,
        'redaction': context['redaction'],
        'instruction': context['instruction'],
        'word_library': context['word_library'],
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_additional_medications.html')
def form_additional_medications(additional_medication_records):
    return {
        'additional_medication_records': additional_medication_records
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_new_additional_medications.html')
def form_new_additional_medications(instruction):
    return {
        'instruction': instruction
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_allergies.html', takes_context=True)
def form_allergies(context):
    return {
        'all_allergies': context['medical_record'].all_allergies,
        'additional_allergies': context['redaction'].additional_allergies,
        'redaction': context['redaction'],
        'instruction': context['instruction'],
        'word_library': context['word_library'],
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_additional_allergies.html')
def form_additional_allergies(additional_allergies_records):
    return {
        'additional_allergies_records': additional_allergies_records
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_new_additional_allergies.html')
def form_new_additional_allergies():
    return {}


@register.inclusion_tag('medicalreport/inclusiontags/redaction_checkbox_with_body.html')
def redaction_checkbox_with_body(model, redaction, header='', body=''):
    checked = ""
    xpaths = model.xpaths()
    snomed_codes = model.snomed_concepts()
    is_sensitive = False
    matched_sensitive_conditions = NhsSensitiveConditions.objects.values_list('snome_code').filter(snome_code__in=snomed_codes)
    if matched_sensitive_conditions:
        checked = "checked"
        is_sensitive = True

    if redaction.redacted(xpaths) is True:
        checked = "checked"

    return {
        'checked': checked,
        'xpaths': xpaths,
        'header': header,
        'header_detail': format_html(header),
        'body': body,
        'is_sensitive': is_sensitive
    }


@register.inclusion_tag('medicalreport/inclusiontags/redaction_checkbox_with_list.html')
def redaction_checkbox_with_list(model, redaction, header='', dict_data='', map_code='', label=None, relations=''):
    checked = ""
    matched_sensitive_conditions = NhsSensitiveConditions.objects.filter(snome_code__in=map_code)
    if redaction.re_redacted_codes:
        matched_sensitive_conditions.filter(~Q(snome_code__in=redaction.re_redacted_codes))
    matched_sensitive_conditions = matched_sensitive_conditions.values_list('snome_code')
    sensitive_conditions = []
    for sensitive_tuple in list(matched_sensitive_conditions):
        sensitive_conditions = [sensitive_code for sensitive_code in sensitive_tuple]

    xpaths = model.xpaths()
    is_sensitive_consultation = False
    for code in map_code:
        if code in sensitive_conditions:
            checked = "checked"
            is_sensitive_consultation = True
    if redaction.redacted(xpaths) is True:
        checked = "checked"
    return {
        'redaction_checks': redaction.redacted_xpaths,
        're_redaced_codes': redaction.re_redacted_codes,
        'checked': checked,
        'relations': relations,
        'xpaths': xpaths,
        'header': header,
        'dict_data': dict_data,
        'label': label,
        'sensitive_conditions': sensitive_conditions,
        'is_sensitive_consultation': is_sensitive_consultation
    }


@register.inclusion_tag('medicalreport/inclusiontags/redaction_checkbox_with_body.html')
def problem_redaction_checkboxes(model, redaction, problem_linked_lists, map_code, header=''):
    checked = ""
    matched_sensitive_conditions = NhsSensitiveConditions.objects.filter(snome_code__in=map_code)
    if redaction.re_redacted_codes:
        matched_sensitive_conditions.filter(~Q(snome_code__in=redaction.re_redacted_codes))
    matched_sensitive_conditions = matched_sensitive_conditions.values_list('snome_code')
    sensitive_conditions = []
    for sensitive_tuple in list(matched_sensitive_conditions):
        sensitive_conditions = [sensitive_code for sensitive_code in sensitive_tuple]

    is_sensitive = False
    for code in map_code:
        if code in sensitive_conditions:
            checked = "checked"
            is_sensitive = True

    xpaths = problem_xpaths(model, problem_linked_lists)
    if redaction.redacted(xpaths) is True:
        checked = "checked"
    return {
        'checked': checked,
        'xpaths': xpaths,
        'header': header,
        'header_detail': format_html(header),
        'is_sensitive': is_sensitive
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_comments.html', takes_context=True)
def form_comments(context):
    return {
        'comment_notes': context['redaction'].comment_notes
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_addition_answers.html', takes_context=True)
def form_addition_answers(context):
    return {
        'questions': context['questions']
    }
