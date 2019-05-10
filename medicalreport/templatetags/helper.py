from django import template

from services.xml.problem import Problem
from django.utils.html import format_html
from datetime import date as Date
from typing import List, Optional
from library.models import Library
register = template.Library()


def format_date(date: Optional[Date]) -> str:
    if date is None:
        return ''
    return date.strftime("%d %b %Y")


def end_date(problem: Problem) -> str:
    parsed_end_date = problem.parsed_end_date()
    if parsed_end_date is None:
        return "(ended: N/A)"
    return "(ended: {})".format(format_date(problem.parsed_end_date()))


def diagnosed_date(problem: Problem, problem_list: List[Problem]) -> str:
    dates = []
    for item in problem_list:
        dates.append(item.parsed_date())

    dates += [problem.parsed_date()]
    date = min(dates)
    if date:
        return "(diagnosed: {})".format(format_date(date))
    else:
        return ''


def additional_medication_dates_description(record):
    dates = []
    if record.prescribed_from:
        text = "from: {}".format(format_date(record.prescribed_from))
        dates += [text]
    if record.prescribed_to:
        text = "to: {}".format(format_date(record.prescribed_to))
        dates += [text]

    if any(dates):
        return "({})".format(' '.join(dates))
    else:
        return ''


def linked_problems(problem, problem_list):
    filterd_list = filter(lambda x: problem.guid() in x.target_guids(), problem_list)
    return list(filterd_list)


def problem_xpaths(problem, problem_link_list):
    problem_link_xpaths = []
    for link in linked_problems(problem, problem_link_list):
        problem_link_xpaths += link.xpaths()

    xpaths = problem.xpaths() + problem_link_xpaths
    return list(set(xpaths))


def generate_toolbox_report(library_history=None, value='', xpath='', instruction=None):
    gp_org = instruction.gp_user.organisation
    library_object = Library.objects.filter(gp_practice=gp_org)
    highlight_html = '''
        <span class="highlight-library">
            <span class="{}">{}</span>
    '''
    if library_history:
        split_word = value.split()
        for word in library_object:
            for history in library_history:
                num = 0
                action = history.action
                while num < len(split_word):
                    if str.upper(split_word[num]) == str.upper(word.key):
                        text = split_word[num]
                        highlight_class = ''
                        if history.old == split_word[num]:
                            if action == 'Replace' and history.xpath in xpath:
                                split_word[num] = history.new
                                text = highlight_html.format(highlight_class, split_word[num])
                            elif action == 'Redact' and history.xpath in xpath:
                                highlight_class = 'bg-dark'
                                text = highlight_html.format(highlight_class, split_word[num])
                            elif action == 'ReplaceAll':
                                split_word[num] = history.new
                                text = highlight_html.format(highlight_class, split_word[num])
                            split_word[num] = format_html(text)
                    num = num + 1
            value = " ".join(split_word)
    return value
                        