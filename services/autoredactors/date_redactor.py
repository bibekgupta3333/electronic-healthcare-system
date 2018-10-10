from services.xml.xml_base import XMLModelBase

from datetime import date


class DateRedactor:
    def __init__(self, start_date: date):
        self.start_date = start_date

    def is_redact(self, model: XMLModelBase) -> bool:
        parsed_date = model.parsed_date()
        if parsed_date and parsed_date < self.start_date:
            return True
        return False
