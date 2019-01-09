from django import template
from medicalreport.templatetags.helper import problem_xpaths

register = template.Library()


@register.inclusion_tag('medicalreport/reports/patient_details.html', takes_context=True)
def patient_details(context):
    return {
        'medical_record': context['medical_record'],
        'instruction': context['instruction']
    }

@register.inclusion_tag('medicalreport/reports/instruction_details.html', takes_context=True)
def instruction_details(context):
    return {
        'dummy_instruction': context['dummy_instruction'],
        'instruction': context['instruction']
    }

@register.inclusion_tag('medicalreport/reports/patient_profile.html', takes_context=True)
def patient_profile(context):
    return {'profile_events': context['medical_record'].profile_events_by_type}

@register.inclusion_tag('medicalreport/reports/significant_conditions.html', takes_context=True)
def significant_conditions(context):
    return {
        'significant_active_problems': context['medical_record'].significant_active_problems,
        'significant_past_problems': context['medical_record'].significant_past_problems,
        'problem_linked_lists': context['medical_record'].problem_linked_lists,
        'redaction': context['redaction']
    }

@register.inclusion_tag('medicalreport/reports/allergies.html', takes_context=True)
def allergies(context):
    return {
        'all_allergies': context['medical_record'].all_allergies,
        'redaction': context['redaction'],
    }

@register.inclusion_tag('medicalreport/reports/consultations.html', takes_context=True)
def consultations(context):
    return {
        'consultations': context['medical_record'].consultations,
        'people': context['medical_record'].people,
        'redaction': context['redaction'],
        'pattern': context['pattern']
    }

@register.inclusion_tag('medicalreport/reports/bloods.html', takes_context=True)
def bloods(context):
    return {
        'results': context['medical_record'].blood_test_results_by_type,
        'redaction': context['redaction']
    }

@register.inclusion_tag('medicalreport/reports/referrals.html', takes_context=True)
def referrals(context):
    return {
        'referrals': context['medical_record'].referrals,
        'locations': context['medical_record'].locations,
        'redaction': context['redaction']
    }

@register.inclusion_tag('medicalreport/reports/medications.html', takes_context=True)
def medications(context):
    return {
        'acute_medications': context['medical_record'].acute_medications,
        'repeat_medications': context['medical_record'].repeat_medications,
        'redaction': context['redaction']
    }

@register.inclusion_tag('medicalreport/reports/appendices.html', takes_context=True)
def appendices(context):
    return {
        'attachments': context['medical_record'].attachments,
        'redaction': context['redaction']
    }

@register.inclusion_tag('medicalreport/reports/comments.html', takes_context=True)
def comments(context):
    return {
        'comment_notes': context['redaction'].comment_notes
    }

@register.inclusion_tag('medicalreport/reports/questions.html', takes_context=True)
def questions(context):
    return {
        'questions': context['instruction'].addition_questions.all()
    }

def get_redaction(model, redaction):
    xpaths = model.xpaths()
    if redaction.redacted(xpaths) is True:
        return True
    return False

def get_xpaths(model, problem_linked_lists):
    return problem_xpaths(model, problem_linked_lists)

def get_redaction_problem_xpaths(xpaths, redaction):
    if redaction.redacted(xpaths) is True:
        return True
    return False

register.filter('get_xpaths', get_xpaths)
register.filter('get_redaction', get_redaction)
register.filter('get_redaction_problem_xpaths', get_redaction_problem_xpaths)
