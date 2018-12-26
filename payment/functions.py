from instructions import model_choices

from instructions.models import Instruction
from .models import InstructionVolumeFee, OrganisationFee


def calculate_instruction_fee(instruction):
    gp_practice = instruction.gp_practice
    time_delta = instruction.completed_signed_off_timestamp - instruction.created
    organisation_fee = OrganisationFee.objects.filter(gp_practice=gp_practice).first()
    organisation_fee_rate = organisation_fee.get_fee_rate(time_delta.days)
    client_organisation = instruction.client_user.organisation
    instruction_volume_fee = InstructionVolumeFee.objects.filter(client_organisation=client_organisation).first()
    if instruction_volume_fee:
        instruction_fee_rate = instruction_volume_fee.get_fee_rate(
            Instruction.objects.filter(client_user__organisation=client_organisation).count()
        )
        vat = instruction_volume_fee.vat
        instruction.medi_earns = instruction_fee_rate + (instruction_fee_rate * (vat / 100))
        if instruction.type == model_choices.AMRA_TYPE:
            instruction.gp_earns = organisation_fee_rate

    instruction.save()
