from .xml_base import XMLModelBase
from .consultation_element import ConsultationElement
from .value_event import ValueEvent


class Consultation(XMLModelBase):
    XPATH = './/Consultation'

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def consultation_elements(self):
        elements = self.parsed_xml.findall(ConsultationElement.XPATH)
        result_list = [ConsultationElement(element) for element in elements]
        return result_list

    def snomed_concepts(self):
        result_list = []
        for element in self.consultation_elements():
            result_list += element.content().snomed_concepts()

        return result_list

    def readcodes(self):
        result_list = []
        for element in self.consultation_elements():
            result_list += element.content().readcodes()

        return result_list

    def original_author_refid(self):
        return self.parsed_xml.find('OriginalAuthor/User/RefID').text

    def is_significant_problem(self):
        return any(element.is_significant_problem() for element in self.consultation_elements())

    def is_profile_event(self):
        return any(element is not None for element in self.parsed_xml.xpath(ValueEvent.XPATH))

    def is_sick_note(self):
        if '9D11.' in self.readcodes():
            return True
        if '1331000000103' in self.snomed_concepts():
            return True
        return False
