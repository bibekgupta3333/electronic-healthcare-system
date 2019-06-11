from django import template
from django.db.models.functions import Length

from services.xml.problem import Problem
from datetime import date as Date
from typing import List, Optional
from library.models import LibraryHistory, Library

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


def render_toolbox_function_for_final_report(library_history: LibraryHistory = None, xpath: str = '', value: str = '', libraries: Library=None, section: str = ''):
    section_library_history = library_history.filter(section=section)
    replace_all_values = {}
    print('-----------------------'+section+'-----------------------')
    print(value)
    for replace_all_history in library_history.filter(action=LibraryHistory.ACTION_REPLACE_ALL):
        # construction dict {'old_word_1': 'new_word_1', 'old_word_2': 'new_word_2', ...}
        replace_all_values[replace_all_history.old] = replace_all_history.new

    splitted_word = value.split()
    final_description = []
    add_orgin_word = True
    if library_history:
        for word in splitted_word:
            if word in replace_all_values:
                final_description.append(replace_all_values[word])
                continue

            for history in section_library_history:
                if str.upper(word) == str.upper(history.old):
                    if history.action == LibraryHistory.ACTION_REPLACE:
                        add_orgin_word = False
                        final_description.append(history.new)
                    elif history.action == LibraryHistory.ACTION_HIGHLIGHT_REDACT:
                        add_orgin_word = False
                        break

            if add_orgin_word:
                final_description.append(word)

        return " ".join(final_description)

    return value
