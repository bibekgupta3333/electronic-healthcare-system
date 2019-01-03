from datetime import date
from ..autoredactors.date_redactor import DateRedactor
from ..autoredactors.conditions_redactor import ConditionsRedactor
from services.xml.xml_base import XMLModelBase
from instructions.models import Instruction

from dateutil.relativedelta import relativedelta
from typing import Iterable, List


def years_ago(years: int, current_date: date) -> date:
    return current_date - relativedelta(years=years)


def auto_redact_by_conditions(
        models: Iterable[XMLModelBase],
        instruction: Instruction
) -> List[XMLModelBase]:
    snomed_concepts_ids, readcodes = instruction.snomed_concepts_ids_and_readcodes()
    redactor = ConditionsRedactor(
        concepts=list(snomed_concepts_ids),
        readcodes=list(readcodes)
    )
    return [m for m in models if not redactor.is_redact(m)]


def auto_redact_by_date(
        models: Iterable[XMLModelBase],
        start_date=None,
        from_date=None,
        to_date=None,
) -> List[XMLModelBase]:
    redactor = DateRedactor(start_date=start_date, from_date=from_date, to_date=to_date)
    return [m for m in models if not redactor.is_redact(m)]


def auto_redact_consultations(consultations, instruction, current_date=date.today()):
    return auto_redact_by_date(
        auto_redact_by_conditions(consultations, instruction),
        start_date=years_ago(5, current_date), from_date=instruction.date_range_from, to_date=instruction.date_range_to
    )


def auto_redact_medications (medications, instruction, current_date=date.today()):
    return auto_redact_by_date(medications, start_date=years_ago(2, current_date), from_date=instruction.date_range_from, to_date=instruction.date_range_to )


def auto_redact_referrals(referrals, instruction, current_date=date.today()):
    return auto_redact_by_date(referrals, start_date=years_ago(5, current_date), from_date=instruction.date_range_from, to_date=instruction.date_range_to )


def auto_redact_attachments(attachments, instruction, current_date=date.today()):
    return auto_redact_by_date(attachments, start_date=years_ago(2, current_date), from_date=instruction.date_range_from, to_date=instruction.date_range_to )


def auto_redact_profile_events(events, instruction, current_date=date.today()):
    return auto_redact_by_date(events, start_date=years_ago(5, current_date), from_date=instruction.date_range_from, to_date=instruction.date_range_to )
