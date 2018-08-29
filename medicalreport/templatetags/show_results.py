from django import template

register = template.Library()


@register.inclusion_tag('medicalreport/inclusiontags/results.html')
def show_results(poll):
    choices = poll.choices
    return {'choices': choices}
