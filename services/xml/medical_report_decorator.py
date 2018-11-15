from .xml_utils import (
    chronological_redactable_elements, alphabetical_redactable_elements
)
from .medical_record import MedicalRecord
from .auto_redactable import (
    auto_redact_referrals, auto_redact_consultations, auto_redact_attachments,
    auto_redact_medications, auto_redact_profile_events,
)
from .xml_base import XMLModelBase
from .consultation import Consultation
from .medication import Medication
from .value_event import ValueEvent
from .problem import Problem
from .referral import Referral
from .attachment import Attachment
from .xml_utils import normalize_data
from instructions.models import Instruction
from instructions import model_choices

from typing import List, Dict, TypeVar
T = TypeVar('T')


class MedicalReportDecorator(MedicalRecord):
    # todo: raw_xml type... string or bytes or something else?
    def __init__(self, raw_xml, instruction: Instruction):
        super().__init__(raw_xml)
        self.instruction = instruction

    def consultations(self) -> List[Consultation]:
        ret_xml = chronological_redactable_elements(super().consultations())
        if self.instruction.type == model_choices.AMRA_TYPE:
            ret_xml = chronological_redactable_elements(
                auto_redact_consultations(
                    super().consultations(),
                    self.instruction
                )
            )
        return ret_xml

    def significant_active_problems(self) -> List[Problem]:
        return alphabetical_redactable_elements(
            super().significant_active_problems()
        )

    def significant_past_problems(self) -> List[Problem]:
        return alphabetical_redactable_elements(
            super().significant_past_problems()
        )

    def referrals(self) -> List[Referral]:
        ret_xml = chronological_redactable_elements(super().referrals())
        if self.instruction.type == model_choices.AMRA_TYPE:
            ret_xml = chronological_redactable_elements(
                auto_redact_referrals(super().referrals())
            )
        return ret_xml

    def attachments(self) -> List[Attachment]:
        ret_xml = chronological_redactable_elements(super().attachments())
        if self.instruction.type == model_choices.AMRA_TYPE:
            ret_xml = chronological_redactable_elements(
                auto_redact_attachments(super().attachments())
            )
        return ret_xml

    def acute_medications(self) -> List[Medication]:
        ret_xml = chronological_redactable_elements(super().acute_medications())
        if self.instruction.type == model_choices.AMRA_TYPE:
            ret_xml = chronological_redactable_elements(
                auto_redact_medications(super().acute_medications())
            )
        return ret_xml

    def repeat_medications(self) -> List[Medication]:
        ret_xml = chronological_redactable_elements(super().acute_medications())
        if self.instruction.type == model_choices.AMRA_TYPE:
            ret_xml = chronological_redactable_elements(
                auto_redact_medications(super().repeat_medications())
            )
        return ret_xml

    def all_allergies(self) -> List[XMLModelBase]:
        return chronological_redactable_elements(super().all_allergies())

    def profile_events_for(self, event_type: str) -> List[XMLModelBase]:
        ret_xml = chronological_redactable_elements(super().acute_medications())
        # if self.instruction.type == model_choices.AMRA_TYPE:
        ret_xml = chronological_redactable_elements(
                auto_redact_profile_events(super().profile_event(event_type))
            )

        return self.__table_elements(ret_xml)

    def profile_events_by_type(self) -> Dict[str, List[XMLModelBase]]:
        obj = {}
        if self.instruction.type == 'AMRA':
            for event_type in self.AMRA__PROFILE_EVENT_TYPES:
                obj[event_type] = self.profile_events_for(event_type)
        else:
            for event_type in self.SAR_PROFILE_EVENT_TYPES:
                obj[event_type] = self.profile_events_for(event_type)
        return normalize_data(obj)

    def bloods_for(self, blood_type: str) -> List[ValueEvent]:
        return self.__table_elements(chronological_redactable_elements(
            super().blood_test(blood_type)
        ))

    def blood_test_results_by_type(self) -> Dict[str, List[ValueEvent]]:
        obj = {}
        for blood_type in ValueEvent.blood_test_types():
            result = self.bloods_for(blood_type)
            if result:
                obj[blood_type] = result
        return obj

    # private
    def __table_elements(self, data: List[T]) -> List[T]:
        element_list = data
        element_list += [None] * (len(element_list))
        return list(reversed(element_list))

    @classmethod
    def __table_blood_elements(cls, data: List[T]) -> List[T]:
        max_len = 3
        element_list = data[:max_len]
        element_list += [None] * (max_len - len(element_list))
        return list(reversed(element_list))
