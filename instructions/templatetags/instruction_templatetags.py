from django import template

register = template.Library()


@register.filter
def keyvalue(dict, key):
    if key in dict:
        return dict[key]


def format_date(date):
    if date is None:
        return ''
    return date.strftime("%H:%M %d %b %Y")


register.filter('format_date', format_date)
