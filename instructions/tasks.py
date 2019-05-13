from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import reverse

from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_PROGRESS

from celery import shared_task

import logging
event_logger = logging.getLogger('medidata.event')


@shared_task(bind=True)
def prepare_medicalreport_data(self, instruction_id):
    """
        1. Keep XML to our DB.
        2. Prepare Relations third party data
        3. Redaction attachment and keep it with instruction
    :return:
    """
    try:
        # TODO implement preparing medical data for edit report

        instruction = Instruction.objects.get(id=instruction_id)
        instruction.status = INSTRUCTION_STATUS_PROGRESS
        instruction.save()

        body_message = 'The redaction processes are now complete for instruction {medi_ref}. ' \
                       'You can now proceed this instruction on this link {hyperlink_pipeline}.'.format(
                            medi_ref=instruction.medi_ref,
                            hyperlink_pipeline=settings.MDX_URL + reverse('instructions:view_pipeline')
                        )

        send_mail(
            'Redaction process now complete for instruction {medi_ref}'.format(medi_ref=instruction_id.medi_ref),
            body_message,
            'MediData',
            [instruction.gp_user.user.email, instruction.gp_practice.organisation_email],
            fail_silently=False
        )
    except Exception as e:
        event_logger.error('Preparing asynchronous medical report data hit and unexpected err (%s).' % repr(e))
