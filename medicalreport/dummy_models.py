from datetime import datetime


class DummyClient(object):
    def __init__(self, company_name):
        self.company_name = company_name


class DummySnomedConcept(object):
    def __init__(self, id, desc):
        self.id = id
        self.fsn_description = desc

    def fsn_description(self):
        return self.fsn_description


class DummyInstruction(object):
    def __init__(self, id, client):
        self.id = id
        self.client = client
        self.selected_snomed_concepts = [
            DummySnomedConcept("523717", "% aggregation (qualifier value)"),
            DummySnomedConcept("534927", "Klinefelter's syndrome XXXY (disorder)"),
            DummySnomedConcept("389755", "XXXXY syndrome (disorder)"),
        ]
