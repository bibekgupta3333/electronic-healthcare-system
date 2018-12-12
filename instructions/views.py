from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.http import HttpRequest, JsonResponse
from django_tables2 import RequestConfig
from .models import Instruction, InstructionAdditionQuestion, InstructionConditionsOfInterest, Setting, InstructionPatient
from .tables import InstructionTable
from .model_choices import *
from .forms import ScopeInstructionForm, AdditionQuestionFormset, SarsConsentForm, MdxConsentForm
from accounts.models import User, GeneralPracticeUser, PracticePreferences
from accounts.models import GENERAL_PRACTICE_USER, CLIENT_USER, MEDIDATA_USER
from accounts.forms import InstructionPatientForm, GPForm
from accounts.functions import create_or_update_patient_user
from organisations.forms import GeneralPracticeForm
from organisations.models import OrganisationGeneralPractice
from organisations.views import get_gporganisation_data
from medicalreport.views import get_matched_patient
from common.functions import multi_getattr
from snomedct.models import SnomedConcept
from permissions.functions import check_permission
from .print_consents import MDXDualConsent

import pytz
from itertools import chain
import ast
import requests
import json

from django.conf import settings
PIPELINE_INSTRUCTION_LINK = settings.PIPELINE_INSTRUCTION_LINK
DUMMY_EMAIL_LIST = settings.DUMMY_EMAIL_LIST
SITE_NAME = settings.SITE_NAME


def count_instructions(user, gp_practice_code, client_organisation):
    naive = parse_datetime("2000-01-1 00:00:00")
    origin_date = pytz.timezone("Europe/London").localize(naive, is_dst=None)
    query_condition = Q(created__gt=origin_date)
    if user.type == GENERAL_PRACTICE_USER:
        if user.userprofilebase.generalpracticeuser.role == GeneralPracticeUser.PRACTICE_MANAGER:
            query_condition = Q(gp_practice_id=gp_practice_code)
        else:
            query_condition = Q(gp_practice_id=gp_practice_code) & (Q(gp_user=user.userprofilebase.generalpracticeuser) | Q(gp_user__isnull=True))
    elif user.type == CLIENT_USER:
        query_condition = Q(client_user__organisation=client_organisation)

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
        'Completed': complete_count,
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
def create_or_update_instruction(request, patient_instruction, scope_form=None, gp_practice=None, instruction_id=None) -> Instruction:
    if instruction_id:
        instruction = get_object_or_404(Instruction, pk=instruction_id)
    else:
        instruction = Instruction()
    if request.user.type == CLIENT_USER:
        instruction.client_user = request.user.userprofilebase.clientuser
        instruction.type = scope_form.cleaned_data['type']
        instruction.gp_practice = gp_practice
        instruction.consent_form = scope_form.cleaned_data['consent_form']
        instruction.gp_title_from_client = request.POST.get('gp_title')
        instruction.gp_initial_from_client = request.POST.get('initial')
        instruction.gp_last_name_from_client = request.POST.get('gp_last_name')
        instruction.date_range_from = scope_form.cleaned_data['date_range_from']
        instruction.date_range_to = scope_form.cleaned_data['date_range_to']

    else:
        instruction.type = SARS_TYPE
        instruction.gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
        instruction.gp_user = request.user.userprofilebase.generalpracticeuser

    instruction.patient_information_id = patient_instruction.id
    instruction.save()

    return instruction


def create_addition_question(instruction, addition_question_formset):
    for form in addition_question_formset:
        if form.is_valid() and form.cleaned_data:
            addition_question = form.save(commit=False)
            addition_question.instruction = instruction
            addition_question.save()


def create_snomed_relations(instruction, condition_of_interests):
    for condition_code in condition_of_interests:
        snomedct = SnomedConcept.objects.filter(external_id=condition_code)
        if snomedct.exists():
            snomedct = snomedct.first()
            InstructionConditionsOfInterest.objects.create(instruction=instruction, snomedct=snomedct)


@login_required(login_url='/accounts/login')
def instruction_pipeline_view(request):
    header_title = "Instructions Pipeline"
    user = request.user

    if user.type == GENERAL_PRACTICE_USER:
        gp_practice = multi_getattr(request, 'user.userprofilebase.generalpracticeuser.organisation', default=None)
        if gp_practice and not gp_practice.is_active():
            return redirect('onboarding:emis_setup', practice_code=gp_practice.pk)

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

    gp_practice_code = multi_getattr(request, 'user.userprofilebase.generalpracticeuser.organisation.pk', default=None)
    client_organisation = multi_getattr(request, 'user.userprofilebase.clientuser.organisation', default=None)
    overall_instructions_number = count_instructions(request.user, gp_practice_code, client_organisation)
    if request.user.type == CLIENT_USER:
        overall_instructions_number = count_instructions(request.user, gp_practice_code, client_organisation)
        instruction_query_set = instruction_query_set.filter(client_user__organisation=client_organisation)

    if request.user.type == GENERAL_PRACTICE_USER:
        gp_role = multi_getattr(request, 'user.userprofilebase.generalpracticeuser.role')
        if gp_role == GeneralPracticeUser.PRACTICE_MANAGER:
            instruction_query_set = instruction_query_set.filter(gp_practice_id=gp_practice_code)
        else:
            instruction_query_set = instruction_query_set.filter(Q(gp_user__user_id=request.user.id) |
                                                                 Q(gp_user__isnull=True), gp_practice_id=gp_practice_code)

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

    if request.method == "POST":
        request.POST._mutable = True
        instruction_id = request.POST.get('instruction_id', None)
        gp_form = GPForm(request.POST)
        addition_question_formset = AdditionQuestionFormset(request.POST)
        raw_common_condition = request.POST.getlist('common_condition')
        common_condition_list = list(chain.from_iterable([ast.literal_eval(item) for item in raw_common_condition]))
        addition_condition_list = request.POST.getlist('addition_condition')
        condition_of_interests = list(set().union(common_condition_list, addition_condition_list))
        scope_form = ScopeInstructionForm(request.user, request.POST.get('patient_email'), request.POST, request.FILES)
        selected_pat_code = request.POST.get('patient_postcode', '')
        selected_pat_adr_num = request.POST.get('patient_address_number', '')
        selected_gp_code = request.POST.get('gp_practice', '')
        selected_gp_name = request.POST.get('gp_practice_name', '')
        selected_add_cond = request.POST.getlist('addition_condition', [])
        selected_add_cond_title = request.POST.get('addition_condition_title', '')
        selected_add_cond_title = selected_add_cond_title.split(',')
        selected_gp_adr_line1 = request.POST.get('patient_address_line1', '')
        selected_gp_adr_line2 = request.POST.get('patient_address_line2', '')
        selected_gp_adr_line3 = request.POST.get('patient_address_line3', '')
        selected_gp_adr_country = request.POST.get('patient_country', '')
        patient_form = InstructionPatientForm(InstructionPatientForm.change_request_date(request.POST))

        i = 0
        while i < len(selected_add_cond):
            selected_add_cond[i] = int(selected_add_cond[i])
            i += 1

        # Is from NHS or gpOrganisation
        gp_practice_code = request.POST.get('gp_practice', None)
        if not gp_practice_code:
            gp_practice_code = multi_getattr(request, 'user.userprofilebase.generalpracticeuser.organisation.pk', default=None)
        gp_practice = OrganisationGeneralPractice.objects.filter(practcode=gp_practice_code).first()
        if (patient_form.is_valid() and scope_form.is_valid() and gp_practice) or\
                (request.user.type == GENERAL_PRACTICE_USER and patient_form.is_valid()):
            if instruction_id:
                prev_instruction = get_object_or_404(Instruction, pk=instruction_id)
                patient_instruction = get_object_or_404(InstructionPatient, instruction=prev_instruction)
                patient_instruction_form = InstructionPatientForm(request.POST, instance=patient_instruction)
                if patient_instruction_form.is_valid():
                    patient_instruction_form.save()
            else:
                patient_instruction = patient_form.save()
            # create instruction
            instruction = create_or_update_instruction(
                request=request, patient_instruction=patient_instruction,
                scope_form=scope_form, gp_practice=gp_practice,
                instruction_id=instruction_id
            )
            practice_preferences = PracticePreferences.objects.get_or_create(gp_organisation=gp_practice)
            if practice_preferences[0].notification == 'NEW':
                send_mail(
                    'New Instruction',
                    'You have a new instruction. Click here {link} to see it.'.format(link=PIPELINE_INSTRUCTION_LINK),
                    'MediData',
                    [gp_practice.organisation_email],
                    fail_silently=True,
                )
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
                    [patient_form.cleaned_data['patient_email']],
                    fail_silently=True,
                )

            if instruction.type == AMRA_TYPE and not instruction.consent_form:
                message = 'Your instruction has request consent form. Please upload or accept consent form in this link {}'\
                    .format(request.get_host() + '/instruction/upload-consent/' + str(instruction.id) + '/')
                send_mail(
                    'Request consent',
                    message,
                    'MediData',
                    [patient_form.cleaned_data['patient_email']],
                    fail_silently=True,
                )

            medidata_emails_list = [user.email for user in User.objects.filter(type=MEDIDATA_USER)]
            gp_emails_list = []
            # Notification: client selected NHS GP
            if not gp_practice.live and not gp_practice.accept_policy:
                send_mail(
                    'NHS GP is selected',
                    'Your client had selected NHS GP: {}'.format(gp_practice.name),
                    'MediData',
                    medidata_emails_list,
                    fail_silently=True,
                )
            else:
                gp_emails_list = [gp.user.email for gp in GeneralPracticeUser.objects.filter(organisation=gp_practice)]

            # Notification: client created new instruction
            send_mail(
                'New Instruction',
                'You have a new instruction. Click here {link} to see it.'.format(link=PIPELINE_INSTRUCTION_LINK),
                'MediData',
                medidata_emails_list + gp_emails_list,
                fail_silently=True,
            )
            messages.success(request, 'Form submission successful')
            if instruction.type == SARS_TYPE and request.user.type == GENERAL_PRACTICE_USER:
                return redirect('instructions:review_instruction', instruction_id=instruction.id)
            else:
                return redirect('instructions:view_pipeline')
        else:
            return render(request, 'instructions/new_instruction.html', {
                'header_title': header_title,
                'patient_form': patient_form,
                'nhs_form': nhs_form,
                'gp_form': gp_form,
                'scope_form': scope_form,
                'addition_question_formset': addition_question_formset,
                'selected_pat_code': selected_pat_code,
                'selected_pat_adr_num': selected_pat_adr_num,
                'selected_gp_code': selected_gp_code,
                'selected_gp_name': selected_gp_name,
                'selected_add_cond': selected_add_cond,
                'selected_add_cond_title': json.dumps(selected_add_cond_title),
                'selected_gp_adr_line1': selected_gp_adr_line1,
                'selected_gp_adr_line2': selected_gp_adr_line2,
                'selected_gp_adr_line3': selected_gp_adr_line3,
                'selected_gp_adr_country': selected_gp_adr_country,
                'GET_ADDRESS_API_KEY': settings.GET_ADDRESS_API_KEY
            })
    patient_form = InstructionPatientForm()
    addition_question_formset = AdditionQuestionFormset(queryset=InstructionAdditionQuestion.objects.none())
    scope_form = ScopeInstructionForm(user=request.user)

    instruction_id = request.GET.get('instruction_id', None)
    if instruction_id:
        instruction = get_object_or_404(Instruction, pk=instruction_id)
        patient_instruction = instruction.patient_information
        # Initial Patient Form
        patient_form = InstructionPatientForm(
            instance=patient_instruction,
            initial={
                'first_name': patient_instruction.patient_first_name,
                'last_name': patient_instruction.patient_last_name,
                'address_postcode': patient_instruction.patient_postcode,
                'edit_patient': True
            }
        )
        # Initial GP/NHS Organisation Form
        if isinstance(instruction.gp_practice, OrganisationGeneralPractice):
            gp_practice_code = instruction.gp_practice.practcode
        else:
            gp_practice_code = instruction.gp_practice.pk
        gp_practice_request = HttpRequest()
        gp_practice_request.GET['code'] = gp_practice_code
        nhs_address = get_gporganisation_data(gp_practice_request, need_dict=True)['address']
        nhs_form = GeneralPracticeForm(
            initial={
                'gp_practice': instruction.gp_practice
            }
        )
        # Initial GP Practitioner Form
        gp_form = GPForm(
            initial={
                'gp_title': instruction.gp_title_from_client,
                'initial': instruction.gp_initial_from_client,
                'gp_last_name': instruction.gp_last_name_from_client,
            }
        )
        # Initial Scope/Consent Form
        scope_form = ScopeInstructionForm(user=request.user, initial={'type': instruction.type, })

        consent_type = 'pdf'
        consent_extension = ''
        consent_path = ''
        if instruction.consent_form:
            consent_extension = (instruction.consent_form.url).split('.')[1]
            consent_path = instruction.consent_form.url
        if consent_extension in ['jpeg', 'png', 'gif']:
            consent_type = 'image'
        consent_form_data = {
            'type': consent_type,
            'path': consent_path
        }

        condition_of_interest = [snomed.fsn_description for snomed in instruction.selected_snomed_concepts()]
        addition_question_formset = AdditionQuestionFormset(queryset=InstructionAdditionQuestion.objects.filter(instruction=instruction))

        return render(request, 'instructions/new_instruction.html', {
            'header_title': header_title,
            'patient_form': patient_form,
            'nhs_form': nhs_form,
            'gp_form': gp_form,
            'scope_form': scope_form,
            'addition_question_formset': addition_question_formset,
            'nhs_address': nhs_address,
            'condition_of_interest': condition_of_interest,
            'consent_form_data': consent_form_data,
            'instruction_id': instruction_id,
            'patient_postcode': patient_instruction.patient_postcode,
            'selected_pat_adr_num': patient_instruction.patient_address_number,
            'selected_gp_adr_line1': patient_instruction.patient_address_line1,
            'selected_gp_adr_line2': patient_instruction.patient_address_line2,
            'selected_gp_adr_line3': patient_instruction.patient_address_line3,
            'selected_gp_adr_country': patient_instruction.patient_country,
            'GET_ADDRESS_API_KEY': settings.GET_ADDRESS_API_KEY
        })
    return render(request, 'instructions/new_instruction.html', {
        'header_title': header_title,
        'patient_form': patient_form,
        'nhs_form': nhs_form,
        'gp_form': gp_form,
        'scope_form': scope_form,
        'addition_question_formset': addition_question_formset,
        'GET_ADDRESS_API_KEY': settings.GET_ADDRESS_API_KEY
    })


def upload_consent(request, instruction_id):
    setting = Setting.objects.all().first()
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    uploaded = False
    if instruction.status != INSTRUCTION_STATUS_NEW:
        uploaded = True
    if request.method == "POST" and setting:
        if request.POST.get('select_type') == 'accept':
            instruction.consent_form = setting.consent_form
        else:
            instruction.consent_form = request.FILES.get('consent_form')
        instruction.save()
        uploaded = True
    return render(request, 'instructions/upload_consent.html',{
            'instruction': instruction,
            'setting': setting,
            'uploaded': uploaded,
        })


@login_required(login_url='/accounts/login')
@check_permission
def review_instruction(request, instruction_id):
    header_title = "Instruction Reviewing"
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    patient_instruction = instruction.patient_information
    date_format = patient_instruction.patient_dob.strftime("%d/%m/%Y")
    # Initial Patient Form
    patient_form = InstructionPatientForm(
        instance=patient_instruction,
        initial={
            'patient_title': patient_instruction.get_patient_title_display(),
            'patient_first_name': patient_instruction.patient_first_name,
            'patient_last_name': patient_instruction.patient_last_name,
            'patient_postcode': patient_instruction.patient_postcode,
            'patient_address_number': patient_instruction.patient_address_number,
            'patient_dob': date_format
        }
    )
    gp_practice_code = instruction.gp_practice.pk
    gp_practice_request = HttpRequest()
    gp_practice_request.GET['code'] = gp_practice_code
    gp_organisation_address = get_gporganisation_data(gp_practice_request, need_dict=True)['address']
    nhs_form = GeneralPracticeForm(
        initial={
            'gp_practice': instruction.gp_practice
        }
    )
    # Initial GP Practitioner Form
    gp_form = GPForm(
        initial={
            'gp_title': instruction.gp_title_from_client,
            'initial': instruction.gp_initial_from_client,
            'gp_last_name': instruction.gp_last_name_from_client,
        }
    )
    # Initial Scope/Consent Form
    scope_form = ScopeInstructionForm(user=request.user, initial={'type': instruction.type, })

    consent_type = 'pdf'
    consent_extension = ''
    consent_path = ''
    if instruction.consent_form:
        consent_extension = (instruction.consent_form.url).split('.')[1]
        consent_path = instruction.consent_form.url
    if consent_extension in ['jpeg', 'png', 'gif']:
        consent_type = 'image'
    consent_form_data = {
        'type': consent_type,
        'path': consent_path
    }

    condition_of_interest = [snomed.fsn_description for snomed in instruction.selected_snomed_concepts()]
    addition_question_formset = AdditionQuestionFormset(queryset=InstructionAdditionQuestion.objects.filter(instruction=instruction))

    return render(request, 'instructions/review_instruction.html', {
        'header_title': header_title,
        'patient_form': patient_form,
        'nhs_form': nhs_form,
        'gp_form': gp_form,
        'scope_form': scope_form,
        'addition_question_formset': addition_question_formset,
        'nhs_address': gp_organisation_address,
        'condition_of_interest': condition_of_interest,
        'consent_form_data': consent_form_data,
        'instruction_id': instruction_id,
        'instruction': instruction
    })


@login_required(login_url='/accounts/login')
@check_permission
def view_reject(request, instruction_id):
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    patient_instruction = instruction.patient_information
    # Initial Patient Form
    patient_form = InstructionPatientForm(
        instance=patient_instruction,
        initial={
            'patient_title': patient_instruction.get_patient_title_display(),
            'patient_first_name': patient_instruction.patient_first_name,
            'patient_last_name': patient_instruction.patient_last_name,
            'patient_postcode': patient_instruction.patient_postcode,
            'patient_address_number': patient_instruction.patient_address_number,
        }
    )
    gp_practice_code = instruction.gp_practice.pk
    gp_practice_request = HttpRequest()
    gp_practice_request.GET['code'] = gp_practice_code
    nhs_address = get_gporganisation_data(gp_practice_request, need_dict=True)['address']
    nhs_form = GeneralPracticeForm(
        initial={
            'gp_practice': instruction.gp_practice
        }
    )
    # Initial GP Practitioner Form
    gp_form = GPForm(
        initial={
            'gp_title': instruction.gp_title_from_client,
            'initial': instruction.gp_initial_from_client,
            'gp_last_name': instruction.gp_last_name_from_client,
        }
    )
    # Initial Scope/Consent Form
    scope_form = ScopeInstructionForm(user=request.user, initial={'type': instruction.type, })

    consent_type = 'pdf'
    consent_extension = ''
    consent_path = ''
    if instruction.consent_form:
        consent_extension = (instruction.consent_form.url).split('.')[1]
        consent_path = instruction.consent_form.url
    if consent_extension in ['jpeg', 'png', 'gif']:
        consent_type = 'image'
    consent_form_data = {
        'type': consent_type,
        'path': consent_path
    }

    condition_of_interest = [snomed.fsn_description for snomed in instruction.selected_snomed_concepts()]
    addition_question_formset = AdditionQuestionFormset(queryset=InstructionAdditionQuestion.objects.filter(instruction=instruction))

    return render(request, 'instructions/view_reject.html', {
        'patient_form': patient_form,
        'nhs_form': nhs_form,
        'gp_form': gp_form,
        'scope_form': scope_form,
        'addition_question_formset': addition_question_formset,
        'nhs_address': nhs_address,
        'condition_of_interest': condition_of_interest,
        'consent_form_data': consent_form_data,
        'instruction': instruction,
        'instruction_id': instruction.id,
    })


@login_required(login_url='/accounts/login')
@check_permission
def consent_contact(request, instruction_id, patient_emis_number):
    instruction = get_object_or_404(Instruction, pk=instruction_id)
    patient_instruction = instruction.patient_information

    if request.method == "POST":
        if request.POST.get('sars_consent_loaded') == 'loaded' and not instruction.sars_consent:
            instruction.sars_consent = request.FILES['sars_consent']
        elif request.POST.get('sars_consent_loaded') != 'loaded':
            instruction.sars_consent.delete()
        if request.POST.get('mdx_consent_loaded') == 'loaded' and not instruction.mdx_consent:
            instruction.mdx_consent = request.FILES['mdx_consent']
        elif request.POST.get('mdx_consent_loaded') != 'loaded':
            instruction.mdx_consent.delete()

        patient_instruction.patient_email = request.POST.get('patient_email', '')
        patient_instruction.patient_telephone_mobile = request.POST.get('patient_telephone_mobile', '')
        patient_instruction.patient_telephone_code = request.POST.get('patient_telephone_code', '')
        patient_instruction.patient_alternate_phone = request.POST.get('patient_alternate_phone', '')
        patient_instruction.patient_alternate_code = request.POST.get('patient_alternate_code', '')
        patient_instruction.save()
        patient_user = create_or_update_patient_user(patient_instruction, patient_emis_number)
        instruction.patient = patient_user
        instruction.save()
        next_step = request.POST.get('next_step', '')
        if next_step == 'view_pipeline':
            instruction.saved = True
            patient_instruction.patient_emis_number = patient_emis_number
            patient_instruction.save()
            gp_user = get_object_or_404(GeneralPracticeUser, user_id=request.user.id)
            instruction.in_progress(context={'gp_user': gp_user})
            return redirect('instructions:view_pipeline')
        elif next_step == 'proceed':
            return redirect('medicalreport:select_patient', instruction_id=instruction_id, patient_emis_number=patient_emis_number)

    patient_email = patient_instruction.patient_email
    patient_telephone_mobile = patient_instruction.patient_telephone_mobile
    patient_alternate_phone = patient_instruction.patient_alternate_phone
    patient_list = get_matched_patient(patient_instruction)
    for patient in patient_list:
        if patient_emis_number == patient.ref_id:
            patient_email = patient_instruction.patient_email
            patient_telephone_mobile = patient.telephone_mobile
            patient_alternate_phone = patient.alternate_phone
    # Initial Patient Form
    patient_form = InstructionPatientForm(
        instance=patient_instruction,
        initial={
            'patient_title': patient_instruction.get_patient_title_display(),
            'patient_first_name': patient_instruction.patient_first_name,
            'patient_last_name': patient_instruction.patient_last_name,
            'patient_postcode': patient_instruction.patient_postcode,
            'patient_address_number': patient_instruction.patient_address_number,
            'patient_email': patient_email,
            'patient_telephone_mobile': patient_telephone_mobile,
            'patient_alternate_phone': patient_alternate_phone
        }
    )
    sars_consent_form = SarsConsentForm()
    mdx_consent_form = MdxConsentForm()

    consent_type = 'pdf'
    consent_extension = ''
    consent_path = ''
    if instruction.sars_consent:
        consent_extension = (instruction.sars_consent.url).split('.')[1]
        consent_path = instruction.sars_consent.url
    if consent_extension in ['jpeg', 'png', 'gif']:
        consent_type = 'image'
    sars_consent_form_data = {
        'type': consent_type,
        'path': consent_path
    }

    consent_type = 'pdf'
    consent_extension = ''
    consent_path = ''
    if instruction.mdx_consent:
        consent_extension = (instruction.mdx_consent.url).split('.')[1]
        consent_path = instruction.mdx_consent.url
    if consent_extension in ['jpeg', 'png', 'gif']:
        consent_type = 'image'
    mdx_consent_form_data = {
        'type': consent_type,
        'path': consent_path
    }

    return render(request, 'instructions/consent_contact.html', {
        'patient_form': patient_form,
        'instruction': instruction,
        'patient_emis_number': patient_emis_number,
        'sars_consent_form': sars_consent_form,
        'mdx_consent_form': mdx_consent_form,
        'sars_consent_form_data': sars_consent_form_data,
        'mdx_consent_form_data': mdx_consent_form_data,
        'reject_types': INSTRUCTION_REJECT_TYPE
    })


@login_required(login_url='/accounts/login')
def print_mdx_consent(request, instruction_id, patient_emis_number):
    instruction = get_object_or_404(Instruction, id=instruction_id)
    patient = instruction.patient_information
    gp_practice = instruction.gp_practice

    params = {
        'patient': patient,
        'gp_practice': gp_practice
    }

    return MDXDualConsent.render(params)


def api_get_address(request, address):
    if not address:
        return JsonResponse({'status': 'error', 'error': 'Address not found.'}, status=404)

    url = 'https://api.getAddress.io/find/' + address + '?api-key=' + settings.GET_ADDRESS_API_KEY
    response = requests.get(url)
    return JsonResponse(response.json())
