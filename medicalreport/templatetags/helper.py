from django import template

from services.xml.problem import Problem

from datetime import date as Date
from typing import List, Optional

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
