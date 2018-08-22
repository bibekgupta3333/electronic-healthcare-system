from .xml_base import XMLModelBase


class Allergy(XMLModelBase):
    XPATH = './/Allergy'

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def description(self):
        display_term = self.parsed_xml.find('DisplayTerm').text
        term = display_term if display_term is not None else self.parsed_xml.find('Code/Term').text
        descriptive_text = self.parsed_xml.find('DescriptiveText').text

        filter_list = filter(None, [term, descriptive_text])
        if filter_list:
            return ', '.join(filter_list)
        else:
            return None
