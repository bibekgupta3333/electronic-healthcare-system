from django.core.mail import send_mail
from django.utils import timezone

from report.models import ThirdPartyAuthorisation

from smtplib import SMTPException
import logging

from django.conf import settings


def report_notification_expired_authorisation_job():
    current_date = timezone.now().date()
    third_party_authorisations = ThirdPartyAuthorisation.objects.all()
    for authorisation in third_party_authorisations:
        if current_date > authorisation.expired_date and not authorisation.expired:
            authorisation.expired = True
            authorisation.save()
            try:
                send_mail(
                    'Medical Report Authorisation',
                    'Your access on SAR report from {patient_name} has been expired. Please contact {patient_name}'.format(
                        patient_name=authorisation.patient_report_auth.patient.user.first_name,
                    ),
                    'MediData',
                    [authorisation.email],
                    fail_silently=True,
                    auth_user=settings.EMAIL_HOST_USER,
                    auth_password=settings.EMAIL_HOST_PASSWORD,
                )
            except SMTPException:
                logging.error('Send mail FAILED to send message')