from instructions import model_choices

from instructions.models import Instruction
from .models import InstructionVolumeFee, GpOrganisationFee

import logging

event_logger = logging.getLogger('medidata.event')


def calculate_instruction_fee(instruction):
    gp_practice = instruction.gp_practice
    time_delta = instruction.completed_signed_off_timestamp - instruction.fee_calculation_start_date
    organisation_fee = GpOrganisationFee.objects.filter(gp_practice=gp_practice).first()
    organisation_fee_rate = 0
    if organisation_fee:
        organisation_fee_rate = organisation_fee.organisation_fee.get_fee_rate(time_delta.days)
    client_organisation = instruction.client_user.organisation if instruction.client_user else None
    instruction_volume_fee = InstructionVolumeFee.objects.filter(client_organisation=client_organisation).first()
    if instruction_volume_fee and organisation_fee:
        instruction_fee_rate = instruction_volume_fee.get_fee_rate(
            Instruction.objects.filter(client_user__organisation=client_organisation).count()
        )
        vat = instruction_volume_fee.vat
        instruction.medi_earns = instruction_fee_rate + (instruction_fee_rate * (vat / 100))
        if instruction.type == model_choices.AMRA_TYPE:
            instruction.gp_earns = organisation_fee_rate

        event_logger.info(
            'fee of instruction ID {instruction_id} has been calculated, medi earns: {medi_earns}, gp earns: {gp_earns}'.format(
                instruction_id=instruction.id,
                medi_earns=instruction.medi_earns,
                gp_earns=instruction.gp_earns,
            )
        )
    instruction.save()
