from datetime import datetime, timedelta
from ..autoredactors.date_redactor import DateRedactor
from ..autoredactors.conditions_redactor import ConditionsRedactor


def years_ago(years, current_date):
    return current_date - timedelta(days=years * 365)


def auto_redact_by_conditions(models, instruction):
    #   snomed_concepts = instruction.external_snomed_concept_ids.map(&:to_s)
    #   puts "====>auto_redact_by_conditions"
    #   puts snomed_concepts
    #   puts "=====auto_redact_by_conditions end"
    #   readcodes = instruction.external_read_codes
    #   puts "====>external_read_codes"
    #   puts readcodes
    #   puts "=====external_read_codes end"
    # snomed_concepts = ['329807003']
    # readcodes = ['EMISSPR410', 'J155.']
    snomed_concepts = []
    readcodes = []
    redactor = ConditionsRedactor(concepts=snomed_concepts, codes=readcodes)
    filtered_list = filter(lambda m: redactor.is_redact(m) is not True, models)
    return list(filtered_list)


def auto_redact_by_date(models, date):
    redactor = DateRedactor(start_date=date)
    filtered_list = filter(lambda m: redactor.is_redact(m) is not True, models)
    return list(filtered_list)


def auto_redact_consultations(consultations, instruction, current_date=datetime.now()):
    return auto_redact_by_date(
        auto_redact_by_conditions(consultations, instruction),
        date=years_ago(5, current_date),
    )


def auto_redact_medications(medications, current_date=datetime.now()):
    return auto_redact_by_date(medications, date=years_ago(2, current_date))


def auto_redact_referrals(referrals, current_date=datetime.now()):
    return auto_redact_by_date(referrals, date=years_ago(5, current_date))


def auto_redact_attachments(attachments, current_date=datetime.now()):
    return auto_redact_by_date(attachments, date=years_ago(5, current_date))


#   def auto_redact_profile_events(events, current_date: Time.zone.today)
#     auto_redact_by_date(
#       events,
#       date: current_date - 5.years,
#     )
#   end
# end
