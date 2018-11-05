class DummyPatient(object):
    def __init__(self, first_name, last_name, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = date_of_birth


class DummyClient(object):
    def __init__(self, company_name):
        self.company_name = company_name


class DummySnomedConcept(object):
    def __init__(self, id, desc):
        self.id = id
        self.fsn_description = desc


class DummyInstruction(object):
    def __init__(self, instruction):
        self.id = instruction.id
        self.consent_form = instruction.consent_form
        self.selected_snomed_concepts = instruction.selected_snomed_concepts()
        if instruction.client_user:
            self.client = DummyClient(instruction.client_user.organisation)
