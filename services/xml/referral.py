from .xml_base import XMLModelBase


class Referral(XMLModelBase):
    XPATH = './/Referral'

    def __str__(self):
        return "Referral"

    def description(self):
        display_term = self.parsed_xml.find('DisplayTerm')
        if display_term is not None:
            display_term = display_term.text

        referral_reason = self.parsed_xml.find('ReferralReason')
        if referral_reason is not None:
            referral_reason = referral_reason.text

        filter_list = list(filter(None, [display_term, referral_reason]))
        if filter_list:
            return ', '.join(filter_list)
        else:
            return 'Referral'

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def provider_refid(self):
        return self.parsed_xml.find('Provider/RefID').text
