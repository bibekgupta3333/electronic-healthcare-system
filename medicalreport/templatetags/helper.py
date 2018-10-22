from django import template
register = template.Library()


def format_date(date):
    if date:
        return date.strftime("%d %b %Y")
    return None


def end_date(problem):
    return "(ended:{})".format(format_date(problem.parsed_end_date()))


def diagnosed_date(problem, problem_list):
    dates = []
    for item in problem_list:
        dates.append(item.parsed_date())

    dates += [problem.parsed_date()]
    date = min(dates)
    if date:
        return "(diagnosed:{})".format(format_date(date))
    else:
        None


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
