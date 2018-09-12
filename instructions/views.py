from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail

from django_tables2 import RequestConfig

from .models import Instruction
from .tables import InstructionTable
from .model_choices import *
from .forms import ScopeInstructionForm
from accounts.models import User, UserProfileBase, Patient, GeneralPracticeUser
from accounts.models import PATIENT_USER
from accounts.forms import PatientForm, GPForm
from organisations.forms import GeneralPracticeForm
from organisations.models import OrganisationGeneralPractice, NHSgpPractice



def count_instructions():
    all_count = Instruction.objects.all().count()
    new_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_NEW).count()
    progress_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_PROGRESS).count()
    overdue_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_OVERDUE).count()
    complete_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_COMPLETE).count()
    rejected_count = Instruction.objects.filter(status=INSTRUCTION_STATUS_REJECT).count()
    overall_instructions_number = {
        'All': all_count,
        'New': new_count,
        'In Progress': progress_count,
        'Overdue': overdue_count,
        'Complete': complete_count,
        'Rejected': rejected_count
    }
    return overall_instructions_number


@login_required(login_url='/accounts/login')
def instruction_pipeline_view(request):
    header_title = "Instructions Pipeline"
    user = request.user

    if 'status' in request.GET:
        filter_type = request.GET.get('type', '')
        filter_status = request.GET.get('status', -1)
        if filter_status == 'undefined':
            filter_status = -1
        else:
            filter_status = int(filter_status)
    else:
        filter_type = request.COOKIES.get('type', '')
        filter_status = int(request.COOKIES.get('status', -1))

    if filter_type and filter_type != 'allType':
        query_set = Instruction.objects.filter(type=filter_type)
    else:
        query_set = Instruction.objects.filter()

    if filter_status != -1:
        query_set = query_set.filter(status=filter_status)

    table = InstructionTable(query_set)

    overall_instructions_number = count_instructions()

    table.order_by = request.GET.get('sort', '-created')
    RequestConfig(request, paginate={'per_page': 5}).configure(table)
    response = render(request, 'instructions/pipeline_views_instruction.html', {
        'user': user,
        'table': table,
        'overall_instructions_number': overall_instructions_number,
        'header_title': header_title
    })

    response.set_cookie('status', filter_status)
    response.set_cookie('type', filter_type)
    return response


@login_required(login_url='/admin')
def new_instruction(request):
    header_title = "Add New Instruction"

    if request.method == "POST":
        scope_form = ScopeInstructionForm(request.POST, request.FILES)
        patient_form = PatientForm(request.POST)
        gp_practice_code = request.POST.get('gp_practice', None)
        gp_practice = OrganisationGeneralPractice.objects.filter(practice_code=gp_practice_code).first()
        if not gp_practice:
            gp_practice = NHSgpPractice.objects.filter(code=gp_practice_code).first()

        if patient_form.is_valid() and scope_form.is_valid() and gp_practice:
            # create patient user
            user = User.objects.create(username="{}.{}".format(patient_form.cleaned_data['first_name'], patient_form.cleaned_data['last_name'][0]),
                                       password="{}.medi2018".format(patient_form.cleaned_data['first_name']),
                                       email=patient_form.cleaned_data['email'],
                                       type=PATIENT_USER,
                                       first_name=patient_form.cleaned_data['first_name'],
                                       last_name=patient_form.cleaned_data['last_name'])
            patient = patient_form.save(commit=False)
            patient.organisation_gp = OrganisationGeneralPractice.objects.first()
            patient.user = user
            patient.save()

            # create instruction
            instruction = Instruction()
            instruction.client_user = request.user.userprofilebase.clientuser
            instruction.patient = patient
            instruction.type = scope_form.cleaned_data['type']
            instruction.consent_form = scope_form.cleaned_data['consent_form']
            instruction.gp_practice = gp_practice
            instruction.save()

            if isinstance(gp_practice, NHSgpPractice):
                send_mail(
                    'NHS GP is selected',
                    'Your client had selected NHS GP: {}'.format(gp_practice.name),
                    'akekatharn@mohara.com',
                    ['lontharn@gmail.com'],
                    fail_silently=False,
                )

            messages.success(request, 'Form submission successful')

    patient_form = PatientForm()
    gp_form = GPForm()
    nhs_form = GeneralPracticeForm()
    scope_form = ScopeInstructionForm()

    return render(request, 'instructions/new_instrcution.html', {
        'header_title': header_title,
        'patient_form': patient_form,
        'nhs_form': nhs_form,
        'gp_form': gp_form,
        'scope_form': scope_form
    }) 