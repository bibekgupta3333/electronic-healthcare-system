from .xml_base import XMLModelBase
from snomedct.models import SnomedConcept, ReadCode


class SocialConsultationElement(XMLModelBase):
    XPATH = ".//ConsultationElement[Header/Term='Social']"

    def date(self) -> str:
        return self.get_element_text('Event/AssignedDate')

    def description(self) -> str:
        return (
            self.get_element_text('Event/DisplayTerm')
            or self.get_element_text('Event/Code/Term')
        )

    def is_smoking(self) -> bool:
        return self.__code_descendent_of(self.__smoking_concept())

    def is_alcohol(self) -> bool:
        return self.__code_descendent_of(self.__alcohol_concept())

    # private
    def __smoking_concept(self) -> SnomedConcept:
        return SnomedConcept.objects.get(external_id='365981007')

    def __alcohol_concept(self) -> SnomedConcept:
        return SnomedConcept.objects.get(external_id='228273003')

    # JT This should really be a model method on SnomedConcept.
    def __code_descendent_of(self, snomed_model: SnomedConcept) -> bool:
        if self.readcodes():
            model_readcodes = map(
                lambda rc: rc.ext_read_code,
                snomed_model.combined_readcodes()
            )
            for rc in self.readcodes():
                if rc in model_readcodes:
                    return True
            return False
        if str(snomed_model.external_id) in self.snomed_concepts():
            return True
        snomed_descendants = snomed_model.snomed_descendants().values('external_id')
        for sc in self.snomed_concepts():
            if int(sc) in snomed_descendants:
                return True
        return False
