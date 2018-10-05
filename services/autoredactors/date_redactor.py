class DateRedactor(object):

    def __init__(self, start_date):
        self.start_date = start_date

    def is_redact(self, model):
        parsed_date = model.parsed_date()
        if parsed_date is not None:
            if parsed_date < self.start_date:
                return True
        return False
