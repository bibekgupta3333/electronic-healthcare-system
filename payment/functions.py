from instructions import model_choices

from django.conf import settings
from instructions.models import Instruction
from .models import InstructionVolumeFee, GpOrganisationFee
from django.core.files.base import ContentFile
from django.template.loader import get_template
from io import BytesIO
import xhtml2pdf.pisa as pisa
import logging
import os

event_logger = logging.getLogger('medidata.event')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = BASE_DIR + '/payment/templates/invoice/instruction_invoice.html'


def calculate_instruction_fee(instruction: Instruction) -> None:
    gp_practice = instruction.gp_practice
    time_delta = instruction.completed_signed_off_timestamp - instruction.fee_calculation_start_date
    organisation_fee = GpOrganisationFee.objects.filter(gp_practice=gp_practice).first()
    organisation_fee_rate = 0
    if organisation_fee:
        organisation_fee_rate = organisation_fee.organisation_fee.get_fee_rate(time_delta.days)
    client_organisation = instruction.client_user.organisation if instruction.client_user else None
    instruction_volume_fee = InstructionVolumeFee.objects.filter(client_org=client_organisation, fee_rate_type=instruction.type_catagory).first()
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


def link_callback(uri: str, rel) -> str:
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT

    if uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        path = sRoot

    if sRoot == 'static':
        path = BASE_DIR + '/medi/' + path

    if not os.path.isfile(path):
        raise Exception('static URI must start with %s' % (sUrl))
    return path


class PaymentInvoice:
    @staticmethod
    def get_invoice_pdf_file(params: dict) -> ContentFile:
        template = get_template(REPORT_DIR)
        html = template.render(params)
        file = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), file, link_callback=link_callback)
        if not pdf.err:
            return ContentFile(file.getvalue())