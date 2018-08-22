from .xml_base import XMLModelBase


class ReferralEvent(XMLModelBase):
    XPATH = ".//Event[EventType='8']"

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def description(self):
        display_term = self.parsed_xml.find('DisplayTerm').text
        descriptive_text = self.parsed_xml.find('DescriptiveText').text

        if display_term:
            return display_term
        elif descriptive_text:
            return descriptive_text
        else:
            return 'Referral'

    def provider_refid(self):
        return None
