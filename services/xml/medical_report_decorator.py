from .xml_utils import chronological_redactable_elements, alphabetical_redactable_elements
from .value_event import ValueEvent
from .medical_record import MedicalRecord
from .auto_redactable import (
    auto_redact_referrals, auto_redact_consultations, auto_redact_attachments,
    auto_redact_medications, auto_redact_profile_events,
)


class MedicalReportDecorator(MedicalRecord):

    def __init__(self, raw_xml, instruction):
        super().__init__(raw_xml)
        self.instruction = instruction

    def consultations(self):
        return chronological_redactable_elements(
            auto_redact_consultations(
                super().consultations(),
                self.instruction
            )
        )

    def significant_active_problems(self):
        return alphabetical_redactable_elements(super().significant_active_problems())

    def significant_past_problems(self):
        return alphabetical_redactable_elements(super().significant_past_problems())

    def referrals(self):
        return chronological_redactable_elements(auto_redact_referrals(super().referrals()))

    def attachments(self):
        return chronological_redactable_elements(auto_redact_attachments(super().attachments()))

    def acute_medications(self):
        return chronological_redactable_elements(auto_redact_medications(super().acute_medications()))

    def repeat_medications(self):
        return chronological_redactable_elements(auto_redact_medications(super().repeat_medications()))

    def all_allergies(self):
        return chronological_redactable_elements(super().all_allergies())

    def profile_events_for(self, type):
        return self.__table_elements(chronological_redactable_elements(auto_redact_profile_events(super().profile_event(type))))

    def profile_events_by_type(self):
        obj = {}
        for event_type in self.PROFILE_EVENT_TYPES:
            obj[event_type] = self.profile_events_for(event_type)
        return obj

    def bloods_for(self, type):
        return self.__table_elements(chronological_redactable_elements(super().blood_test(type)))

    def blood_test_results_by_type(self):
        obj = {}
        for blood_type in ValueEvent.blood_test_types():
            result = self.bloods_for(blood_type)
            if any(result):
                obj[blood_type] = result
        return obj

    # private
    def __table_elements(self, data):
        max_len = 3
        element_list = data[:max_len]
        element_list += [None] * (max_len - len(element_list))
        return list(reversed(element_list))
