from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.forms import ValidationError

from django_tables2 import RequestConfig

from .models import Instruction, InstructionAdditionQuestion, InstructionConditionsOfInterest
from .tables import InstructionTable
from .model_choices import *
from .forms import ScopeInstructionForm, AdditionQuestionFormset
from accounts.models import User, Patient, GeneralPracticeUser
from accounts.models import PATIENT_USER, GENERAL_PRACTICE_USER, CLIENT_USER, MEDIDATA_USER
from accounts.forms import PatientForm, GPForm
from organisations.forms import GeneralPracticeForm
from organisations.models import OrganisationGeneralPractice, NHSgpPractice
from template.forms import TemplateInstructionForm
from common.functions import multi_getattr, get_env_variable

from django.conf import settings
PIPELINE_INSTRUCTION_LINK = settings.PIPELINE_INSTRUCTION_LINK
DUMMY_EMAIL_LIST = settings.DUMMY_EMAIL_LIST

from snomedct.models import SnomedConcept

import pytz
from itertools import chain
import ast


def count_instructions(gp_practice_id, client_organisation, medidata=False):
    naive = parse_datetime("2000-01-1 00:00:00")
    origin_date = pytz.timezone("Europe/London").localize(naive, is_dst=None)
    query_condition = Q(created__gt=origin_date)
    if not medidata:
        query_condition = Q(gp_practice_id=gp_practice_id) | Q(client_user__organisation=client_organisation)

    all_count = Instruction.objects.filter(query_condition).count()
    new_count = Instruction.objects.filter(query_condition, status=INSTRUCTION_STATUS_NEW).count()
    progress_count = Instruction.objects.filter(query_condition, status=INSTRUCTION_STATUS_PROGRESS).count()
    overdue_count = Instruction.objects.filter(query_condition, status=INSTRUCTION_STATUS_OVERDUE).count()
    complete_count = Instruction.objects.filter(query_condition, status=INSTRUCTION_STATUS_COMPLETE).count()
    rejected_count = Instruction.objects.filter(query_condition, status=INSTRUCTION_STATUS_REJECT).count()
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


def create_instruction(user, patient, scope_form=None, gp_practice=None) -> Instruction:
    instruction = Instruction()
    if user.type == CLIENT_USER:
        instruction.client_user = user.userprofilebase.clientuser
        instruction.type = scope_form.cleaned_data['type']
        instruction.gp_practice = gp_practice
        instruction.consent_form = scope_form.cleaned_data['consent_form']
    else:
        instruction.type = SARS_TYPE
        instruction.gp_practice = user.userprofilebase.generalpracticeuser.organisation
        instruction.gp_user = user.userprofilebase.generalpracticeuser

    instruction.patient = patient
    instruction.save()

    return instruction


def create_addition_question(instruction, addition_question_formset):
    for form in addition_question_formset:
        if form.is_valid():
            addition_question = form.save(commit=False)
            addition_question.instruction = instruction
            addition_question.save()


def create_snomed_relations(instruction, condition_of_interests):
    for condition_code in condition_of_interests:
        snomedct = SnomedConcept.objects.get(external_id=condition_code)
        InstructionConditionsOfInterest.objects.create(instruction=instruction, snomedct=snomedct)


def create_patient_user(request, patient_form, patient_email) -> Patient:
    # find existing user if no create patient user
    user = User.objects.filter(
        Q(username="{}.{}".format(patient_form.cleaned_data['first_name'], patient_form.cleaned_data['last_name'][0])) |
        Q(email=patient_email), type=PATIENT_USER
    ).first()

    if not user:
        user = User.objects.create(
            username="{}.{}".format(patient_form.cleaned_data['first_name'], patient_form.cleaned_data['last_name'][0]),
            password="{}.medi2018".format(patient_form.cleaned_data['first_name']),
            email=patient_email,
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
        patient = Patient.objects.get(user=user)
        messages.warning(request, 'Patient Existing In Database')

    return patient


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
    overall_instructions_number = count_instructions(gp_practice_id, client_organisation, medidata=True)
    if request.user.type in [GENERAL_PRACTICE_USER, CLIENT_USER]:
        instruction_query_set = instruction_query_set.filter(Q(gp_practice_id=gp_practice_id) |
                                                             Q(client_user__organisation=client_organisation))
        overall_instructions_number = count_instructions(gp_practice_id, client_organisation)

    table = InstructionTable(instruction_query_set)
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

    gp_form = GPForm()
    nhs_form = GeneralPracticeForm()
    template_form = TemplateInstructionForm()

    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        addition_question_formset = AdditionQuestionFormset(request.POST)
        raw_common_condition = request.POST.getlist('common_condition')
        common_condition_list = list(chain.from_iterable([ast.literal_eval(item) for item in raw_common_condition]))
        addition_condition_list = request.POST.getlist('addition_condition')
        condition_of_interests = list(set().union(common_condition_list, addition_condition_list))
        scope_form = ScopeInstructionForm(request.user, request.POST.get('email'), request.POST, request.FILES)

        # Is from NHS or gpOrganisation
        gp_practice_code = request.POST.get('gp_practice', None)
        gp_practice = OrganisationGeneralPractice.objects.filter(practice_code=gp_practice_code).first()
        if not gp_practice:
            gp_practice = NHSgpPractice.objects.filter(code=gp_practice_code).first()

        if (patient_form.is_valid() and scope_form.is_valid() and gp_practice) or request.user.type == GENERAL_PRACTICE_USER:

            patient_email = patient_form.cleaned_data['email'] if patient_form.cleaned_data['email'] else "{}.{}@medidata.com".format(
                patient_form.cleaned_data['first_name'], patient_form.cleaned_data['last_name'][0]
            )

            # create patient user
            patient = create_patient_user(request, patient_form, patient_email)
            # create instruction
            instruction = create_instruction(user=request.user, patient=patient, scope_form=scope_form, gp_practice=gp_practice)
            if request.user.type == CLIENT_USER:
                # create relations of instruction with snomed code
                create_snomed_relations(instruction, condition_of_interests)
                # create addition question
                create_addition_question(instruction, addition_question_formset)
            else:
                send_mail(
                    'Patient Notification',
                    'Your instruction has been created',
                    'MediData',
                    [patient_email],
                    fail_silently=False,
                )

            medidata_emails_list = [user.email for user in User.objects.filter(type=MEDIDATA_USER)]
            gp_emails_list = []
            # Notification: client selected NHS GP
            if isinstance(gp_practice, NHSgpPractice):
                send_mail(
                    'NHS GP is selected',
                    'Your client had selected NHS GP: {}'.format(gp_practice.name),
                    'MediData',
                    medidata_emails_list,
                    fail_silently=False,
                )
            else:
                gp_emails_list = [gp.user.email for gp in GeneralPracticeUser.objects.filter(organisation=gp_practice)]

            # Notification: client created new instruction
            send_mail(
                'New Instruction',
                'You have a new instruction. Click here {link} to see it.'.format(link=PIPELINE_INSTRUCTION_LINK),
                'MediData',
                medidata_emails_list + gp_emails_list,
                fail_silently=False,
            )
        else:
            messages.error(request, scope_form.errors['__all__'].data[0].messages[0])
            return render(request, 'instructions/new_instruction.html', {
                'header_title': header_title,
                'patient_form': patient_form,
                'nhs_form': nhs_form,
                'gp_form': gp_form,
                'scope_form': scope_form,
                'addition_question_formset': addition_question_formset,
                'template_form': template_form,
            })
    patient_form = PatientForm()
    addition_question_formset = AdditionQuestionFormset(queryset=InstructionAdditionQuestion.objects.none())
    scope_form = ScopeInstructionForm(user=request.user)

    return render(request, 'instructions/new_instruction.html', {
        'header_title': header_title,
        'patient_form': patient_form,
        'nhs_form': nhs_form,
        'gp_form': gp_form,
        'scope_form': scope_form,
        'addition_question_formset': addition_question_formset,
        'template_form': template_form,
    })