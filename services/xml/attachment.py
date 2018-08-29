from .xml_base import XMLModelBase


class Attachment(XMLModelBase):
    XPATH = './/Attachment'
    DESCRIPTION_XPATHS = ['DescriptiveText', 'DisplayTerm', 'Code/Term']

    def __str__(self):
        return "Attachment"

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def description(self):
        for xpath in self.DESCRIPTION_XPATHS:
            desc = self.parsed_xml.find(xpath)
            if desc is not None:
                return desc.text
        return 'Attachment'

    def dds_identifier(self):
        return self.parsed_xml.find('DDSIdentifier').text

    def to_param(self):
        return self.dds_identifier()

    def xpaths(self):
        xpath = ".//ConsultationElement[Attachment/GUID='{}']".format(self.guid())
        return xpath
