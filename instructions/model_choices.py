AMRA_TYPE = 'AMRA'
SARS_TYPE = 'SARS'

INSTRUCTION_TYPE_CHOICES = (
    (AMRA_TYPE, 'AMRA'),
    (SARS_TYPE, 'SARS')
)


INSTRUCTION_STATUS_NEW = 0
INSTRUCTION_STATUS_PROGRESS = 1
INSTRUCTION_STATUS_OVERDUE = 2
INSTRUCTION_STATUS_COMPLETE = 3
INSTRUCTION_STATUS_REJECT = 4

INSTRUCTION_STATUS_CHOICES = (
    (INSTRUCTION_STATUS_NEW, 'New'),
    (INSTRUCTION_STATUS_PROGRESS, 'In Progress'),
    (INSTRUCTION_STATUS_OVERDUE, 'Overdue'),
    (INSTRUCTION_STATUS_COMPLETE, 'Completed'),
    (INSTRUCTION_STATUS_REJECT, 'Rejected')
)

PATIENT_NOT_FOUND = 0
PATIENT_NO_LONGER_REGISTERED = 1
CONSENT_INVALID = 2
INAPPROPRIATE_SAR = 3
INSTRUCTION_REJECT_TYPE = (
    (PATIENT_NOT_FOUND, 'No suitable patient can be found'),
    (PATIENT_NO_LONGER_REGISTERED, 'The patient is no longer registered at this practice'),
    (CONSENT_INVALID, 'The consent form is invalid'),
    (INAPPROPRIATE_SAR, 'Inappropriate purpose for Subject Access Request')
)
