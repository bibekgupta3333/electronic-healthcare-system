from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from instructions.forms import TemplateInstructionForm
from common.functions import multi_getattr
from .models import TemplateInstruction, TemplateAdditionalQuestion, TemplateConditionsOfInterest, \
                    TemplateCommonCondition, TemplateAdditionCondition
from .forms import TemplateAdditionalQuestionForm, TemplateAdditionalQuestionFormset
from permissions.functions import access_template
from snomedct.models import SnomedConcept, CommonSnomedConcepts

from itertools import chain
import ast


def create_template_instruction(request):
    temp_instruction = TemplateInstruction()
    temp_instruction.template_title = request.POST.get('template_title')
    temp_instruction.type = request.POST.get('type')
    temp_instruction.description = request.POST.get('description')
    temp_instruction.save()
    return temp_instruction


def create_or_update_addition_question(temp_instruction, addition_question_formset, request):
    TemplateAdditionalQuestion.objects.filter(template_instruction=temp_instruction).delete()
    for form in addition_question_formset:
        form.full_clean()
        if form.cleaned_data['question'] != '':
            TemplateAdditionalQuestion.objects.create(
                template_instruction=temp_instruction,
                question=form.cleaned_data['question']
            )


def create_or_update_addition_question_ajax(temp_instruction, request):
    TemplateAdditionalQuestion.objects.filter(template_instruction=temp_instruction).delete()
    questions = request.POST.getlist('questions[]')
    for question in questions:
        if question:
            TemplateAdditionalQuestion.objects.create(template_instruction=temp_instruction, question=question)


def create_or_update_snomed_relations(temp_instruction, common_condition_list, addition_condition_list):
    TemplateCommonCondition.objects.filter(template_instruction=temp_instruction).delete()
    TemplateAdditionCondition.objects.filter(template_instruction=temp_instruction).delete()
    for common_condition_id in common_condition_list:
        common_condition = CommonSnomedConcepts.objects.get(pk=common_condition_id)
        TemplateCommonCondition.objects.create(template_instruction=temp_instruction, common_condition=common_condition)
    for condition_code in addition_condition_list:
        snomedct = SnomedConcept.objects.filter(external_id=condition_code)
        if snomedct.exists():
            snomedct = snomedct.first()
            TemplateAdditionCondition.objects.create(template_instruction=temp_instruction, snomedct=snomedct)


@access_template
def template_create_or_update(request, temp_instruction=None):
    if request.is_ajax():
        common_condition_list = request.POST.getlist('common_condition[]')
        addition_condition_list = request.POST.getlist('addition_condition[]')

        # create or update template
        if temp_instruction is None:
            temp_instruction = create_template_instruction(request)
            temp_instruction.organisation = request.user.userprofilebase.clientuser.organisation
            temp_instruction.save()
        # create or update relations of instruction with snomed code
        create_or_update_snomed_relations(temp_instruction, common_condition_list, addition_condition_list)
        # create or update addition question
        create_or_update_addition_question_ajax(temp_instruction, request)
        return JsonResponse({'state': 'success'})
    
    template_form = TemplateInstructionForm(request.POST)
    if template_form.is_valid():
        addition_question_formset = TemplateAdditionalQuestionFormset(request.POST)
        common_condition_list = request.POST.getlist('common_condition')
        addition_condition_list = request.POST.getlist('addition_condition')
        # create template
        if temp_instruction is None:
            temp_instruction = create_template_instruction(request)
            temp_instruction.created_by = request.user.userprofilebase.clientuser
            temp_instruction.save()
        # create relations of instruction with snomed code
        create_or_update_snomed_relations(temp_instruction, common_condition_list, addition_condition_list)
        # create addition question
        create_or_update_addition_question(temp_instruction, addition_question_formset, request)
        messages.success(request, 'Template successfully saved.')
        return JsonResponse({'state': 'success'})


@access_template
def template_views(request):
    header_title = "View Templates"
    templates = TemplateInstruction.objects.filter(created_by=request.user.userprofilebase.clientuser)

    return render(request, 'template/template_list.html', {
        'header_title': header_title,
        'templates': templates
    })


@access_template
def template_new(request):
    header_title = "New Template"
    template_form = TemplateInstructionForm()
    addition_question_formset = TemplateAdditionalQuestionFormset(queryset=TemplateAdditionalQuestion.objects.none())
    if request.method == 'POST':
        template_create_or_update(request)
        return redirect('template:view_templates')

    return render(request, 'template/template_new.html', {
        'header_title': header_title,
        'template_form': template_form,
        'addition_question_formset': addition_question_formset
    })


@access_template
def template_edit(request, template_id):
    header_title = "Edit Template"
    template_instruction = TemplateInstruction.objects.get(pk=template_id)

    if request.method == "POST":
        template_create_or_update(request, template_instruction)
        return redirect('template:view_templates')
    
    template_questions = TemplateAdditionalQuestion.objects.filter(template_instruction=template_instruction)
    template_common_conditions = TemplateCommonCondition.objects.filter(template_instruction=template_instruction)
    template_addition_conditions = TemplateAdditionCondition.objects.filter(template_instruction=template_instruction)

    conditions = []
    for template_common_condition in template_common_conditions:
        conditions.append({
            "id": str(template_common_condition.common_condition.pk),
            "text": template_common_condition.common_condition.common_name,
            "is_common_condition": "True"
        })
    for template_addition_condition in template_addition_conditions:
        conditions.append({
            "id": str(template_addition_condition.snomedct.pk),
            "text": template_addition_condition.snomedct.fsn_description,
            "is_common_condition": "False"
        })

    template_form = TemplateInstructionForm(initial={
        "template_title": template_instruction.template_title,
        "type": template_instruction.type
    })
    addition_question_formset = TemplateAdditionalQuestionFormset(queryset=template_questions)

    return render(request, 'template/template_edit.html', {
        'header_title': header_title,
        'template_form': template_form,
        'template_id': template_id,
        'conditions': conditions,
        'addition_question_formset': addition_question_formset
    })


def template_remove(request):
    if request.method == "POST":
        template_id = request.POST.get('template_id', None)
        template_instruction = TemplateInstruction.objects.get(pk=template_id)
        template_instruction.delete()
        messages.success(request, 'Template successfully deleted.')
        return JsonResponse({'state': 'success'})


def template_autocomplete(request):
    search_param = request.GET.get('search', None)
    author = request.user.userprofilebase.clientuser
    query = TemplateInstruction.objects.filter(Q(created_by=author) | Q(organisation=author.organisation))
    if search_param:
        query = query.filter(template_title__icontains=search_param)

    response = []
    templates = query.values('pk', 'template_title')

    for template in templates:
        response.append({
            'id': template['pk'],
            'text': template['template_title']
        })
    return JsonResponse(response, status=200, safe=False)


def get_template_data(request):
    template_title = request.GET.get('template_title')
    response = {'questions': [], 'conditions': []}
    if template_title:
        template_instruction = TemplateInstruction.objects.get(template_title=template_title)
        template_questions = TemplateAdditionalQuestion.objects.filter(template_instruction=template_instruction)
        template_common_conditions = TemplateCommonCondition.objects.filter(template_instruction=template_instruction)
        template_addition_conditions = TemplateAdditionCondition.objects.filter(template_instruction=template_instruction)
        
        for question in template_questions:
            response['questions'].append({
                "id": question.pk,
                "text": question.question
            })
        
        for template_common_condition in template_common_conditions:
            response['conditions'].append({
                "id": str(template_common_condition.common_condition.pk),
                "text": template_common_condition.common_condition.common_name,
                "is_common_condition": "True"
            })

        for template_addition_condition in template_addition_conditions:
            response['conditions'].append({
                "id": str(template_addition_condition.snomedct.pk),
                "text": template_addition_condition.snomedct.fsn_description,
                "is_common_condition": "False"
            })
        
        return JsonResponse(response, status=200, safe=False)
