from .xml_base import XMLModelBase
from .consultation_element import ConsultationElement


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

    def original_author_refid(self):
        return self.parsed_xml.find('OriginalAuthor/User/RefID').text
