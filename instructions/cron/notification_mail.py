from django.core.mail import send_mail
from django.utils import timezone
from django.shortcuts import reverse
from django.db.models import Q
from instructions.models import Instruction, InstructionReminder
from instructions.model_choices import *
from accounts.models import User, PracticePreferences, GeneralPracticeUser
from common.functions import get_url_page
from datetime import timedelta

from smtplib import SMTPException
import logging

from django.conf import settings


def instruction_notification_email_job():
    instruction_notification_sars()


def instruction_notification_amra():
    instruction_query_set = Instruction.objects.filter(type='AMRA')
    instruction_query_set = instruction_query_set.filter(~Q(status=INSTRUCTION_STATUS_COMPLETE) & ~Q(status=INSTRUCTION_STATUS_REJECT) & ~Q(status=INSTRUCTION_STATUS_PAID))

     # Get Value for table range 3 days.
    expected_date_3days = timezone.now() - timedelta(days=3)
    to_expected_date_3days = expected_date_3days.replace(hour=23, minute=59, second=59)
    from_expected_date_3days = expected_date_3days.replace(hour=00, minute=00, second=00)
    instruction_query_set_3days = Q(created__range=(from_expected_date_3days, to_expected_date_3days))

    # Get Value for table range 7 days.
    expected_date_7days = timezone.now() - timedelta(days=7)
    to_expected_date_7days = expected_date_7days.replace(hour=23, minute=59, second=59)
    from_expected_date_7days = expected_date_7days.replace(hour=00, minute=00, second=00)
    instruction_query_set_7days = Q(created__range=(from_expected_date_7days, to_expected_date_7days))

    # Get Value for table range 11 days.
    expected_date_11days = timezone.now() - timedelta(days=11)
    to_expected_date_11days = expected_date_11days.replace(hour=23, minute=59, second=59)
    from_expected_date_11days = expected_date_11days.replace(hour=00, minute=00, second=00)
    instruction_query_set_11days = Q(created__range=(from_expected_date_11days, to_expected_date_11days))

    instruction_query_set = instruction_query_set.filter(instruction_query_set_3days | instruction_query_set_7days | instruction_query_set_11days)


def instruction_notification_sars():
    now = timezone.now()
    new_or_pending_instructions = Instruction.objects.filter(
        status__in=(INSTRUCTION_STATUS_NEW, INSTRUCTION_STATUS_PROGRESS),
        type=SARS_TYPE
    )

    date_period_admin = [3, 7, 14]
    date_period_surgery = [7, 14, 21, 30]
    for instruction in new_or_pending_instructions:
        diff_date = now - instruction.created
        if diff_date.days in date_period_admin or diff_date.days in date_period_surgery:
            gp_managers = User.objects.filter(
                userprofilebase__generalpracticeuser__organisation=instruction.gp_practice.pk,
                userprofilebase__generalpracticeuser__role=GeneralPracticeUser.PRACTICE_MANAGER
            ).values('email')
            try:
                if gp_managers and diff_date.days in date_period_admin:
                    send_mail(
                        'Pending Instruction',
                        'You have a pending or not started instruction. Click here {link} to see it.'.format(
                            link=settings.MDX_URL + reverse('instructions:view_pipeline')
                        ),
                        'MediData',
                        [gp['email'] for gp in gp_managers],
                        fail_silently=True,
                        auth_user=settings.EMAIL_HOST_USER,
                        auth_password=settings.EMAIL_HOST_PASSWORD,
                    )
                if instruction.gp_practice and instruction.gp_practice.organisation_email and diff_date.days in date_period_surgery:
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
    unstarted_instructions = Instruction.objects.filter(status=INSTRUCTION_STATUS_NEW)
    for instruction in unstarted_instructions:
        gp_practice = instruction.gp_practice
        practice_preferences = PracticePreferences.objects.get(gp_organisation=gp_practice)
        if practice_preferences.notification == 'DIGEST':
            send_mail(
                'Unstarted Instruction',
                'You have unstarted instructions. Click here {link} to see it.'.format(link=settings.MDX_URL + reverse('instructions:view_pipeline')),
                'MediData',
                [gp_practice.organisation_email],
                fail_silently=True,
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD,
            )
