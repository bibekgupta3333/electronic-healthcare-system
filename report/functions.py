
from django.core.mail import send_mail
from django.template import loader



#todo add link
def send_patient_mail(patient, gp_practice):
    send_mail(
        'Completely eMR',
        'Your instruction has been submitted',
        'MediData',
        [patient.email],
        fail_silently=True,
        html_message=loader.render_to_string('medicalreport/patient_email.html',
                                             {
                                                 'name': patient.first_name,
                                                 'gp': gp_practice.name,
                                                 'link': 'just a link'
                                             }
                                             )
    )
