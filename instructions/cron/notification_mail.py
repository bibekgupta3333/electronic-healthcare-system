from django.core.mail import send_mail
from django.utils import timezone

from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS
from accounts.models import User
from medi.settings.common import PIPELINE_INSTRUCTION_LINK
from medi.settings.common import get_env_variable

from smtplib import SMTPException
import logging


def instruction_notification_email_job():
    now = timezone.now()
    new_or_pending_instructions = Instruction.objects.filter(
        status__in=(INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS), gp_practice_type__model='organisationgeneralpractice'
    )

    for instruction in new_or_pending_instructions:
        diff_date = now - instruction.created
        if diff_date.days == 3 or diff_date.days == 7 or diff_date.days >= 14:
            gp_managers = User.objects.filter(
                userprofilebase__generalpracticeuser__organisation=instruction.gp_practice_id,
                is_staff=True
            ).values('email')

            try:
                send_mail(
                    'New Instruction',
                    ' You have a pending or not started instruction. Click here {link} to see it.'.format(link=PIPELINE_INSTRUCTION_LINK),
                    'mohara.qr@gmail.com',
                    [gp['email'] for gp in gp_managers],
                    fail_silently=False,
                    auth_user=get_env_variable('SENDGRID_USER'),
                    auth_password=get_env_variable('SENDGRID_PASS'),
                )
            except SMTPException:
                logging.error('Send mail FAILED to send message')