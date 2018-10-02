from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q

from django_tables2 import RequestConfig

from .models import Instruction, InstructionAdditionQuestion, InstructionConditionsOfInterest
from .tables import InstructionTable
from .model_choices import *
from .forms import ScopeInstructionForm, AdditionQuestionFormset
from accounts.models import User, Patient
from accounts.models import PATIENT_USER
from accounts.forms import PatientForm, GPForm
from organisations.forms import GeneralPracticeForm
from organisations.models import OrganisationGeneralPractice, NHSgpPractice
from common.functions import multi_getattr
from medi.settings.common import PIPELINE_INSTRUCTION_LINK, get_env_variable, DUMMY_EMAIL_LIST
from snomedct.models import SnomedConcept


def count_instructions(gp_practice_id, client_organisation):
    all_count = Instruction.objects.filter(
        Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation)).count()
    new_count = Instruction.objects.filter(
        Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation),
        status=INSTRUCTION_STATUS_NEW).count()
    progress_count = Instruction.objects.filter(
        Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation),
        status=INSTRUCTION_STATUS_PROGRESS).count()
    overdue_count = Instruction.objects.filter(
        Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation),
        status=INSTRUCTION_STATUS_OVERDUE).count()
    complete_count = Instruction.objects.filter(
        Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation),
        status=INSTRUCTION_STATUS_COMPLETE).count()
    rejected_count = Instruction.objects.filter(
        Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation),
        status=INSTRUCTION_STATUS_REJECT).count()
    overall_instructions_number = {
        'All': all_count,
        'New': new_count,
        'In Progress': progress_count,
        'Overdue': overdue_count,
        'Complete': complete_count,
        'Rejected': rejected_count
    }
    return overall_instructions_number


def calculate_next_prev(page=None, **kwargs):
    if not page:
        return {
            'next_disabled': 'disabled',
            'prev_disabled': 'disabled'
        }
    else:
        prev_disabled = ""
        next_disabled = ""
        if page.number <= 1:
            prev_page = 1
            prev_disabled = "disabled"
        else:
            prev_page = page.number - 1

        if page.number >= page.paginator.num_pages:
            next_disabled = "disabled"
            next_page = page.paginator.num_pages
        else:
            next_page = page.number + 1

        return {
            'next_page': next_page, 'prev_page': prev_page,
            'status': kwargs['filter_status'], 'type': kwargs['filter_type'],
            'next_disabled': next_disabled, 'prev_disabled': prev_disabled
        }


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

        if filter_type == 'undefined':
            filter_type = 'allType'
    else:
        filter_type = request.COOKIES.get('type', '')
        filter_status = int(request.COOKIES.get('status', -1))

    if filter_type and filter_type != 'allType':
        instruction_query_set = Instruction.objects.filter(type=filter_type)
    else:
        instruction_query_set = Instruction.objects.all()

    if filter_status != -1:
        instruction_query_set = instruction_query_set.filter(status=filter_status)

    gp_practice_id = multi_getattr(request, 'user.userprofilebase.generalpracticeuser.organisation.id', default=None)
    client_organisation = multi_getattr(request, 'user.userprofilebase.clientuser.organisation', default=None)
    instruction_query_set = instruction_query_set.filter(Q(gp_practice_id=gp_practice_id) |
                                                         Q(client_user__organisation=client_organisation))
    table = InstructionTable(instruction_query_set)
    overall_instructions_number = count_instructions(gp_practice_id, client_organisation)
    table.order_by = request.GET.get('sort', '-created')
    RequestConfig(request, paginate={'per_page': 5}).configure(table)

    response = render(request, 'instructions/pipeline_views_instruction.html', {
        'user': user,
        'table': table,
        'overall_instructions_number': overall_instructions_number,
        'header_title': header_title,
        'next_prev_data': calculate_next_prev(table.page, filter_status=filter_status, filter_type=filter_type)
    })

    response.set_cookie('status', filter_status)
    response.set_cookie('type', filter_type)
    return response


@login_required(login_url='/accounts/login')
def new_instruction(request):
    header_title = "Add New Instruction"

    if request.method == "POST":
        scope_form = ScopeInstructionForm(request.user, request.POST, request.FILES,)
        patient_form = PatientForm(request.POST)
        addition_question_formset = AdditionQuestionFormset(request.POST)
        common_condition_list = request.POST.getlist('common_condition')
        addition_condition_list = request.POST.getlist('addition_condition')
        condition_of_interests = common_condition_list + addition_condition_list

        # Is from NHS or gpOrganisation
        gp_practice_code = request.POST.get('gp_practice', None)
        gp_practice = OrganisationGeneralPractice.objects.filter(practice_code=gp_practice_code).first()
        if not gp_practice:
            gp_practice = NHSgpPractice.objects.filter(code=gp_practice_code).first()

        if patient_form.is_valid() and scope_form.is_valid() and gp_practice:
            # find existing user if no create patient user
            user = User.objects.filter(
                Q(username="{}.{}".format(patient_form.cleaned_data['first_name'], patient_form.cleaned_data['last_name'][0])) |
                Q(email=patient_form.cleaned_data['email'])
            )
            if not user.exists():
                user = User.objects.create(
                    username="{}.{}".format(patient_form.cleaned_data['first_name'], patient_form.cleaned_data['last_name'][0]),
                    password="{}.medi2018".format(patient_form.cleaned_data['first_name']),
                    email=patient_form.cleaned_data['email'],
                    type=PATIENT_USER,
                    first_name=patient_form.cleaned_data['first_name'],
                    last_name=patient_form.cleaned_data['last_name']
                )
                patient = patient_form.save(commit=False)
                patient.organisation_gp = OrganisationGeneralPractice.objects.first()
                patient.user = user
                patient.save()
                messages.success(request, 'Form submission successful')
            else:
                patient = Patient.objects.get(user__in=user)
                messages.warning(request, 'Patient Existing In Database')

            # create instruction
            instruction = Instruction()
            instruction.client_user = request.user.userprofilebase.clientuser
            instruction.patient = patient
            instruction.type = scope_form.cleaned_data['type']
            instruction.consent_form = scope_form.cleaned_data['consent_form']
            instruction.gp_practice = gp_practice
            instruction.save()

            for condition_code in condition_of_interests:
                snomedct = SnomedConcept.objects.get(external_id=condition_code)
                InstructionConditionsOfInterest.objects.create(instruction=instruction, snomedct=snomedct)

            for form in addition_question_formset:
                if form.is_valid():
                    addition_question = form.save(commit=False)
                    addition_question.instruction = instruction
                    addition_question.save()

            # Notification: client selected NHS GP
            if isinstance(gp_practice, NHSgpPractice):
                send_mail(
                    'NHS GP is selected',
                    'Your client had selected NHS GP: {}'.format(gp_practice.name),
                    'MediData',
                    DUMMY_EMAIL_LIST,
                    fail_silently=False,
                )

            # Notification: client created new instruction
            send_mail(
                'New Instruction',
                'You have a new instruction. Click here {link} to see it.'.format(link=PIPELINE_INSTRUCTION_LINK),
                'mohara.qr@gmail.com',
                DUMMY_EMAIL_LIST,
                fail_silently=False,
                auth_user=get_env_variable('SENDGRID_USER'),
                auth_password=get_env_variable('SENDGRID_PASS'),
            )

    patient_form = PatientForm()
    gp_form = GPForm()
    nhs_form = GeneralPracticeForm()
    addition_question_formset = AdditionQuestionFormset(queryset=InstructionAdditionQuestion.objects.none())
    scope_form = ScopeInstructionForm(user=request.user)

    return render(request, 'instructions/new_instrcution.html', {
        'header_title': header_title,
        'patient_form': patient_form,
        'nhs_form': nhs_form,
        'gp_form': gp_form,
        'scope_form': scope_form,
        'addition_question_formset': addition_question_formset,
    }) 