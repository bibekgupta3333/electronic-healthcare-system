from .xml_base import XMLModelBase
from ..dummy_models import DummySnomedConcept


class SocialConsultationElement(XMLModelBase):
    XPATH = ".//ConsultationElement[Header/Term='Social']"

    def date(self):
        self.parsed_xml.find('Event/AssignedDate').text

    def description(self):
        display_term = self.parsed_xml.find('Event/DisplayTerm').text
        term = self.parsed_xml.find('Event/Code/Term').text
        if display_term is not None:
            return display_term
        else:
            return term

    def is_smoking(self):
        self.__code_descendent_of(self.__smoking_concept())

    def is_alcohol(self):
        self.__code_descendent_of(self.__alcohol_concept())

    # private
    def __smoking_concept(self):
        # SnomedConcept.active.find_by(external_id: '365981007')
        return DummySnomedConcept()

    def __alcohol_concept(self):
        # SnomedConcept.active.find_by(external_id: '228273003')
        return DummySnomedConcept()

    def __code_descendent_of(self, parent):
        if self.readcodes():
            pass
            # parent.descendant_readcodes.active.where(ext_read_code: readcodes).exists?
        else:
            pass
            # parent.descendant_snomed_concepts.active.where(external_id: snomed_concepts).exists?
