from itertools import chain
import ast

from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from common.functions import multi_getattr
from .forms import (
    TemplateInstructionForm, TemplateInstructionAdditionalQuestionForm, TemplateConditionsOfInterestForm,
    TemplateInstructionAdditionalQuestionFormset, TemplateConditionsOfInterestFormset
)
from .models import (
    TemplateInstruction, TemplateInstructionAdditionalQuestion, TemplateConditionsOfInterest
)


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form.
    """
    def form_invalid(self, form):
        if self.request.is_ajax():
            data = {
                'pk': None,
                'errors': form.errors
            }
            return data
        else:
            response = super().form_invalid(form)
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        self.object = form.save()

        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'errors': {}
            }
            return data
        else:
            response = super().form_valid(form)
            return response


class TemplateCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    form_class = TemplateInstructionForm
    http_method_names = ['post']
    raise_exception = True

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        template_instruction_data = {
            'title': self.request.POST.get('title'),
            'description': self.request.POST.get('description'),
            'created_by': self.request.user.pk,
            'client_organisation': multi_getattr(self.request.user, 'userprofilebase.clientuser.organisation', default=None)
        }

        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': template_instruction_data,
                'files': self.request.FILES,
            })
        return kwargs

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response['errors']:
            return JsonResponse(response, status=400)
        template_instruction_id = response['pk']

        # save questions
        questions = request.POST.getlist('questions[]')
        for question in questions:
            data = {
                'question': question,
                'template_instruction': template_instruction_id
            }
            template_questions_form = TemplateInstructionAdditionalQuestionForm(data=data)
            if template_questions_form.is_valid():
                template_questions_form.save()

        # save conditions
        raw_common_condition = request.POST.getlist('common_conditions[]')
        common_condition_list = list(chain.from_iterable([ast.literal_eval(item) for item in raw_common_condition]))
        addition_condition_list = request.POST.getlist('addition_conditions')
        condition_of_interests = list(set().union(common_condition_list, addition_condition_list))
        for condition in condition_of_interests:
            data = {
                'snomedct': condition,
                'template_instruction': template_instruction_id
            }
            template_conditions_form = TemplateConditionsOfInterestForm(data=data)
            if template_conditions_form.is_valid():
                template_conditions_form.save()

        return JsonResponse(response)


class TemplateList(LoginRequiredMixin, ListView):
    http_method_names = ['get']
    model = TemplateInstruction
    template_name = 'template/template_list.html'
    paginate_by = 5


    def get_context_data(self, **kwargs):
        object_list = self.model.objects.filter(created_by=self.request.user).\
            prefetch_related('templateinstructionadditionalquestion_set')
        context = super().get_context_data(object_list=object_list)
        return context


class TemplateEdit(LoginRequiredMixin, UpdateView):
    template_name = 'template/template_edit.html'
    model = TemplateInstruction
    form_class = TemplateInstructionForm
    success_url = reverse_lazy('template:list')

    def get_context_data(self, **kwargs):

        self.get_object()
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['questions_formset'] = TemplateInstructionAdditionalQuestionFormset(self.request.POST,
                                                                                        instance=self.object)
            context['questions_formset'].full_clean()

            context['conditions_formset'] = TemplateConditionsOfInterestFormset(self.request.POST,
                                                                                        instance=self.object)
            context['conditions_formset'].full_clean()
        else:
            context['questions_formset'] = TemplateInstructionAdditionalQuestionFormset(instance=self.object)
            context['conditions_formset'] = TemplateConditionsOfInterestFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        questions_formset = context['questions_formset']
        conditions_formset = context['conditions_formset']
        if conditions_formset.is_valid() and questions_formset.is_valid():
            self.object = form.save()
            conditions_formset.instance = self.object
            questions_formset.instance = self.object
            conditions_formset.save()
            questions_formset.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class TemplateSearch(LoginRequiredMixin, ListView):
    raise_exception = True
    model = TemplateInstruction
    http_method_names = ['get']

    def get_queryset(self):
        search_param = self.request.GET.get('title', None)
        qs = super().get_queryset()
        client_organisation = multi_getattr(self.request.user, 'userprofilebase.clientuser.organisation', default=None)
        qs = qs.filter(Q(client_organisation=client_organisation) | Q(client_organisation__isnull=True))
        if search_param:
            qs = qs.filter(title__icontains=search_param)
        return qs

    def get(self, request, *args, **kwargs):
        templates = self.get_queryset().values('pk', 'title')
        response = []
        for item in templates:
            response.append({
                "id": item['pk'],
                "text": item['title'],
            })
        return JsonResponse(response, status=200, safe=False)


class TemplateDetails(LoginRequiredMixin, DetailView):
    raise_exception = True
    model = TemplateInstruction
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        template_instruction = self.get_object()
        template_questions = TemplateInstructionAdditionalQuestion.objects.filter(template_instruction=template_instruction)
        template_conditions = TemplateConditionsOfInterest.objects.filter(template_instruction=template_instruction)
        response = {'questions': [], 'conditions': []}

        for question in template_questions:
            response['questions'].append({
                "id": question.pk,
                "text": question.question,
            })

        for condition in template_conditions:
            response['conditions'].append({
                "id": str([condition.snomedct.pk]),
                "text": condition.snomedct.fsn_description,
                "is_common_condition": bool(condition.snomedct.commonsnomedconcepts_set.count()),
            })

        return JsonResponse(response, status=200, safe=False)
