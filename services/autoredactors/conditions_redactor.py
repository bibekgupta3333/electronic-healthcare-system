class ConditionsRedactor(object):

    def __init__(self, concepts=[], codes=[]):
        self.concepts = concepts
        self.codes = codes

    def is_redact(self, model):
        if self.has_any_codes(model) is True:
            if self.snomed_concepts_match(model) is False and self.readcodes_match(model) is False:
                return True
        return False

    def has_any_codes(self, model):
        if not self.concepts and not self.codes:
            return False
        if model.snomed_concepts() or model.readcodes():
            return True
        return False

    def snomed_concepts_match(self, model):
        if model.snomed_concepts():
            for concept in model.snomed_concepts():
                if int(concept) in self.concepts:
                    return True
        return False

    def readcodes_match(self, model):
        if model.readcodes():
            for code in model.readcodes():
                if code in self.codes:
                    return True
        return False
