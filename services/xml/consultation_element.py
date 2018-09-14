from .xml_base import XMLModelBase
from .value_event import ValueEvent
from .referral_event import ReferralEvent
from .allergy_event import AllergyEvent
from .attachment import Attachment
from .medication import Medication
from .referral import Referral
from .allergy import Allergy
from .problem import Problem


class GenericContent(XMLModelBase):
    XPATH = '*[last()]'

    def __str__(self):
        return "GenericContent"

    def description(self):
        display_term = self.parsed_xml.find('DisplayTerm')
        code_term = self.parsed_xml.find('Code/Term')
        term = None
        if display_term is not None:
            term = display_term.text
        elif code_term is not None:
            term = code_term.text

        descriptive_text = self.parsed_xml.find('DescriptiveText')
        if descriptive_text is not None:
            descriptive_text = descriptive_text.text

        filter_list = list(filter(None, [term, descriptive_text]))

        if filter_list is not None:
            return ', '.join(filter_list)
        else:
            return None


class ConsultationElement(XMLModelBase):
    XPATH = './/ConsultationElement'
    CONTENT_CLASSES = [
        ValueEvent,
        ReferralEvent,
        AllergyEvent,
        Attachment,
        Medication,
        Referral,
        Allergy,
    ]

    def header(self):
        return self.parsed_xml.find('Header/Term').text

    def display_order(self):
        display_order = self.parsed_xml.find('DisplayOrder')
        if display_order is not None:
            return int(display_order.text)
        else:
            return -1

    def content(self):
        for klass in self.CONTENT_CLASSES:
            element = self.parsed_xml.find(klass.XPATH)
            if element is not None:
                return klass(element)

        generic_content = self.parsed_xml.xpath(GenericContent.XPATH)[0]
        return GenericContent(generic_content)

    def problem(self):
        problem = self.content().parsed_xml.xpath('.//Problem')
        if problem:
            return Problem(self.content().parsed_xml)
        else:
            return None

    def is_significant_problem(self):
        problem = self.problem()
        if problem is not None:
            return problem.is_significant()
        else:
            False
