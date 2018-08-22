from .xml_base import XMLModelBase


class AllergyEvent(XMLModelBase):
    XPATH = ".//Event[EventType='11']"

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def description(self):
        display_term = self.parsed_xml.find('DisplayTerm').text
        descriptive_text = self.parsed_xml.find('DescriptiveText').text

        if display_term:
            return display_term
        else:
            return descriptive_text
