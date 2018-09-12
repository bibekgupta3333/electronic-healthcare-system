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


class DummyAdditionalAllergies(object):
    def __init__(self, id, allergen, reaction, date_discovered):
        self.id = id
        self.allergen = allergen
        self.reaction = reaction
        self.date_discovered_str = date_discovered

    def date_discovered(self):
        return datetime.strptime(self.date_discovered_str, "%d/%m/%Y")


class DummyAdditionalMedicationRecords(object):
    def __init__(self, id, drug, dose, frequency, snomed_concept_id, redaction_id, prescribed_from, prescribed_to, notes, repeat):
        self.id = id
        self.drug = drug
        self.dose = dose
        self.frequency = frequency
        self.snomed_concept_id = snomed_concept_id
        self.redaction_id = redaction_id
        self.prescribed_from_str = prescribed_from
        self.prescribed_to_str = prescribed_to
        self.notes = notes
        self.repeat = repeat
        self.snomed_concept = DummySnomedConcept("1234", "snomed description")

    def prescribed_from(self):
        return datetime.strptime(self.prescribed_from_str, "%d/%m/%Y")

    def prescribed_to(self):
        return datetime.strptime(self.prescribed_to_str, "%d/%m/%Y")


class DummyRedaction(object):
    def __init__(self):
        self.instruction = DummyInstruction()
        self.redacted_xpaths = [
            ".//ConsultationElement[Referral/GUID='{1FA96ED4-14F8-4322-B6F5-E00262AE124D}']",
            ".//ConsultationElement[Attachment/GUID='{6BC4493F-DB5F-4C74-B585-05B0C3AA53C9}']",
            ".//Consultation[GUID='{94DAFC52-26F4-4341-BFDB-397FA67C17E2}']",
            ".//Event[GUID='{13021918-0B2B-44E7-AC28-A6643D4CFEC9}']",
            ".//Medication[GUID='{A85327B8-3106-480A-BDD3-0777D0F267D1}']"
        ]

    def redacted(self, xpaths):
        return all(xpath in self.redacted_xpaths for xpath in xpaths)

    def additional_acute_medications(self):
        return [DummyAdditionalMedicationRecords('1', 'drug', 'dose', 'frequency', 'snomed_concept_id', 'redaction_id', '23/08/2015', '23/09/2015', 'notes', 'acute')]

    def additional_repeat_medications(self):
        return [DummyAdditionalMedicationRecords('2', 'drug', 'dose', 'frequency', 'snomed_concept_id', 'redaction_id', '23/08/2015', '23/09/2015', 'notes', 'repeat')]

    def additional_allergies(self):
        return [DummyAdditionalAllergies('3', 'xxxxx', 'yyyyy', '23/08/2015')]