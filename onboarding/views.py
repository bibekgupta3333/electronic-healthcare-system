from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.core.mail import send_mail
from onboarding.forms import EMRSetupForm
from instructions.models import Setting
from django.conf import settings


def emr_setup(request):
    emr_form = EMRSetupForm()
    created = False

    if request.method == "POST":
        emr_form = EMRSetupForm(request.POST)
        if emr_form.is_valid():
            emr = emr_form.save()
            send_email_emr(request, emr)
            created = True

    return render(request, 'onboarding/emr_setup.html', {
        'emr_form': emr_form,
        'created': created
    })

def send_email_emr(request, emr):
    setting = Setting.objects.all().first()
    if setting:
        from_email = settings.DEFAULT_FROM
        to_list = [emr.pm_email]
        html_message = loader.render_to_string('onboarding/emr_email.html',{
            'link': '{}/onboarding/emr_setup_stage_2/{}'.format(setting.site, emr.id)
        })
        send_mail('Completely eMR','',from_email,to_list,fail_silently=True,html_message=html_message)
