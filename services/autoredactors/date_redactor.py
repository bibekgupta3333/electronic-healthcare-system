class DateRedactor(object):

    def __init__(self, start_date):
        self.start_date = start_date

    def is_redact(self, model):
        if model.parsed_date() is not None:
            if model.parsed_date() < self.start_date:
                return True
        return False
