from .xml_base import XMLModelBase
import re


class Medication(XMLModelBase):
    XPATH = './/Medication'
    DATE_XPATHS = ['DateLastIssue', 'AssignedDate']
    DESCRIPTION_XPATHS = ['Drug/PreparationID/Term', 'Dosage', 'QuantityRepresentation']

    def __str__(self):
        return "Medication "

    def date(self):
        for xpath in self.DATE_XPATHS:
            date_val = self.parsed_xml.find(xpath)
            if date_val is not None:
                return date_val.text
        return None

    def description(self):
        desc_list = []
        for index, xpath in enumerate(self.DESCRIPTION_XPATHS):
            desc = self.parsed_xml.find(xpath)
            if desc is not None:
                desc = desc.text

            if index is 0 and desc is None:
                desc = 'Medication'

            if desc is not None:
                desc_list.append(desc)

        return ', '.join(desc_list)

    def issue_count(self):
        return self.parsed_xml.find('IssueCount').text

    def parsed_issue_count(self):
        return int(self.issue_count())

    def prescription_type(self):
        return self.parsed_xml.find('PrescriptionType').text

    def is_repeat(self):
        result = re.match('(REPEAT|AUTOMATIC)', self.prescription_type(), re.IGNORECASE)
        if result:
            return True
        else:
            return False

    def is_acute(self):
        result = re.match('ACUTE', self.prescription_type(), re.IGNORECASE)
        if result:
            return True
        else:
            return False

    def snomed_concepts(self):
        snomed_concept = self.parsed_xml.find("Drug/PreparationID[Scheme='SNOMED']/Value")
        mapped_snomed_concept = self.parsed_xml.find("Drug/PreparationID[Scheme='EMISPREPARATION'][MapScheme='SNOMED']/MapCode")

        if snomed_concept is not None:
            return [snomed_concept.text]
        if mapped_snomed_concept is not None:
            return [mapped_snomed_concept.text]
        return []

    def readcodes(self):
        readcode = self.parsed_xml.find("Drug/PreparationID[Scheme='READ2']/Value")
        mapped_readcode = self.parsed_xml.find("Drug/PreparationID[Scheme='EMISPREPARATION'][MapScheme='READ2']/MapCode")

        if readcode is not None:
            return [readcode.text]
        if mapped_readcode is not None:
            return [mapped_readcode.text]
        return []

    def is_significant_problem(self):
        return False

    def is_profile_event(self):
        return False
