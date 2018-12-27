from django.core.mail import send_mail
from django.utils import timezone

from instructions.models import Instruction, InstructionReminder
from instructions.model_choices import INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS
from accounts.models import User, PracticePreferences, GeneralPracticeUser
from common.functions import get_url_page

from smtplib import SMTPException
import logging

from django.conf import settings


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
                userprofilebase__generalpracticeuser__role=GeneralPracticeUser.PRACTICE_MANAGER
            ).values('email')
            try:
                send_mail(
                    'Pending Instruction',
                    'You have a pending or not started instruction. Click here {link} to see it.'.format(
                        link=get_url_page('instruction_pipeline')
                    ),
                    'MediData',
                    [gp['email'] for gp in gp_managers],
                    fail_silently=True,
                    auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD,
                )
                if instruction.gp_practice and instruction.gp_practice.organisation_email:
                    send_mail(
                        'Pending Instruction',
                        'You have a pending or not started instruction.',
                        'MediData',
                        [instruction.gp_practice.organisation_email],
                        fail_silently=True,
                        auth_user=settings.EMAIL_HOST_USER,
                        auth_password=settings.EMAIL_HOST_PASSWORD,
                    )
                InstructionReminder.objects.create(
                    instruction_id=instruction.id,
                    note="note added to instruction for %s day reminder"%diff_date.days,
                    reminder_day=diff_date.days
                )
            except SMTPException:
                logging.error('Send mail FAILED to send message')


def send_email_to_practice_job():
    unstarted_instructions = Instruction.objects.filter(status=INSTRUCTION_STATUS_NEW, gp_practice_type__model='organisationgeneralpractice')
    for instruction in unstarted_instructions:
        gp_practice = instruction.gp_practice
        practice_preferences = PracticePreferences.objects.get(gp_organisation=gp_practice)
        if practice_preferences.notification == 'DIGEST':
            send_mail(
                'Unstarted Instruction',
                'You have unstarted instructions. Click here {link} to see it.'.format(link=get_url_page('instruction_pipeline')),
                'MediData',
                [gp_practice.organisation_email],
                fail_silently=True,
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD,
            )
