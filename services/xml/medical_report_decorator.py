from .xml_utils import chronological_redactable_elements
from .medical_record import MedicalRecord
from .auto_redactable import (
    auto_redact_referrals, auto_redact_consultations, auto_redact_attachments,
    auto_redact_medications,
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

    def referrals(self):
        return chronological_redactable_elements(auto_redact_referrals(super().referrals()))

    def attachments(self):
        return chronological_redactable_elements(auto_redact_attachments(super().attachments()))

    def acute_medications(self):
        return chronological_redactable_elements(auto_redact_medications(super().acute_medications()))
