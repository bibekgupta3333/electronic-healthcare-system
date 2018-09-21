from .xml_base import XMLModelBase
from snomedct.models import SnomedConcept


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
        return SnomedConcept.objects.get(external_id='365981007')

    def __alcohol_concept(self):
        return SnomedConcept.objects.get(external_id='228273003')

    def __code_descendent_of(self, snomed_model):
        if self.readcodes():
            result = snomed_model.objects.filter(readcodes__ext_read_code__in=self.readcodes())
            if result:
                return True
            else:
                return False
            # parent.descendant_readcodes.active.where(ext_read_code: readcodes).exists?
        else:
            result = snomed_model.objects.filter(snomeddescendant__external_id=self.snomed_concepts())
            if result:
                return True
            else:
                return False
            # parent.descendant_snomed_concepts.active.where(external_id: snomed_concepts).exists?
