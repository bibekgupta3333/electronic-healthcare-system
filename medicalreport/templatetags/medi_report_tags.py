from django import template

register = template.Library()


@register.inclusion_tag('medicalreport/inclusiontags/patient_info.html', takes_context=True)
def patient_info(context):
    return {
        'medical_record': context['medical_record'],
        'instruction': context['redaction'].instruction
    }


@register.inclusion_tag('medicalreport/inclusiontags/form_referrals.html', takes_context=True)
def form_referrals(context):
    return {
        'referrals': context['medical_record'].referrals,
        'locations': context['medical_record'].locations,
        'redaction': context['redaction']
    }


@register.inclusion_tag('medicalreport/inclusiontags/redaction_checkbox.html')
def redaction_checkbox(model, redaction, header):
    checked = ""
    if redaction.redacted(model.xpaths()) is True:
        checked = "checked"
    return {
        'checked': checked,
        'xpath': model.xpaths(),
        'header': header
    }
