from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_tables2 import RequestConfig
from django.db.models import Q
from django.db import IntegrityError
from django.http import JsonResponse

from instructions.views import calculate_next_prev

from .models import Library, LibraryHistory
from .tables import LibraryTable
from .forms import LibraryForm
from instructions.models import Instruction


@login_required(login_url='/accounts/login')
def edit_library(request, event):
    header_title = "Surgery Library"
    page_length = 10
    search_input = ''
    gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
    library = Library.objects.filter(gp_practice=gp_practice)
    library_form = LibraryForm(gp_org_id=gp_practice.pk)
    add_word_error_message = ''
    edit_word_error_message = ''
    error_edit_link = ''
    if request.method == 'POST':
        library_form = LibraryForm(request.POST, gp_org_id=gp_practice.pk)
        event = ''
        if library_form.is_valid():
            library_obj = library_form.save(commit=False)
            library_obj.gp_practice = gp_practice
            library_obj.save()
            library_form = LibraryForm(gp_org_id=gp_practice.pk)
            if event == 'add' and request.is_ajax():
                return JsonResponse({'message': 'A word has been created.'})
            messages.success(request, 'Add word successfully')
        else:
            add_word_error_message = 'This word already exist in your library. If you wish to edit it, please go back ' \
                                      'to the library and edit from there'
            if event == 'add' and request.is_ajax():
                return JsonResponse({'message': 'Error', 'add_word_error_message': add_word_error_message})
        event = ''

    if 'page_length' in request.GET:
        page_length = int(request.GET.get('page_length'))

    if 'search' in request.GET:
        search_input = request.GET.get('search')
        library = library.filter(Q(key__icontains=search_input) | Q(value__icontains=search_input))
        event = 'index'

    if event.split(':')[0] == 'edit_error':
        error_edit_id = event.split(':')[1]
        error_libray = Library.objects.get(id=error_edit_id)
        library_form = LibraryForm(instance=error_libray)
        error_edit_link = reverse('library:edit_word_library', kwargs={'library_id': error_edit_id})
        edit_word_error_message = 'This word already exist in your library. If you wish to edit it, please go back ' \
                                  'to the library and edit from there'

    table = LibraryTable(library)
    RequestConfig(request, paginate={'per_page': page_length}).configure(table)
    next_prev_data = calculate_next_prev(table.page,  page_length=page_length)

    return render(request, 'library/edit_library.html', {
        'header_title': header_title,
        'table': table,
        'next_prev_data': next_prev_data,
        'page_length': page_length,
        'search_input': search_input,
        'library_form': library_form,
        'event': event,
        'add_word_error_message': add_word_error_message,
        'edit_word_error_message': edit_word_error_message,
        'error_edit_link': error_edit_link
    })


@login_required(login_url='/accounts/login')
def delete_library(request, library_id):
    library = get_object_or_404(Library, pk=library_id)
    library.hard_delete()

    return redirect('library:edit_library', event='delete')


@login_required(login_url='/accounts/login')
def edit_word_library(request, library_id):
    library = get_object_or_404(Library, pk=library_id)
    library.key = request.POST.get('key')
    library.value = request.POST.get('value')
    event = 'edit'
    try:
        library.save()
        messages.success(request, 'Update word successfully')
    except IntegrityError as e:
        event = 'edit_error:{id}'.format(id=library.id)

    return redirect('library:edit_library', event=event)


@login_required(login_url='/accounts/login')
def redact_word(request):
    if request.is_ajax():
        try:
            word = request.GET.get('word').strip()
            instruction_id = request.GET.get('instruction_id')
            header = request.GET.get('header')
            index = request.GET.get('index')
            content = request.GET.get('content')
            xpath = request.GET.get('xpath')

            gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
            library = Library.objects.filter(gp_practice=gp_practice).filter(key=word).first()

            change_info = '%s :-> %s :-> %s' % (header.strip(), index, content.strip())
            instruction = Instruction.objects.get(pk=instruction_id)
            library_history = LibraryHistory(
                instruction= instruction,
                action= 'Redact',
                old= word,
                new= '',
                change_info= change_info,
                xpath= xpath,
            )
            library_history.save()
            return JsonResponse({'redact_word': library.value, 'id': library_history.id})
        except:
            return JsonResponse({'message': 'Error'})


@login_required(login_url='/accounts/login')
def replace_word(request):
    if request.is_ajax():
        try:
            word = request.GET.get('word').strip()
            instruction_id = request.GET.get('instruction_id')
            header = request.GET.get('header')
            index = request.GET.get('index')
            content = request.GET.get('content')
            xpath = request.GET.get('xpath')
            gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
            library = Library.objects.filter(gp_practice=gp_practice).filter(key=word).first()

            change_info = '%s :-> %s :-> %s' % (header.strip(), index, content.strip())
            instruction = Instruction.objects.get(pk=instruction_id)
            library_history = LibraryHistory(
                instruction= instruction,
                action= 'Replace',
                old= word,
                new= library.value,
                change_info= change_info,
                xpath= xpath,
            )
            library_history.save()
            return JsonResponse({'replace_word': library.value, 'id': library_history.id})
        except:
            return JsonResponse({'message': 'Error'})

@login_required(login_url='/accounts/login')
def replace_allword(request):
    if request.is_ajax():
        try:
            word = request.GET.get('word').strip()
            instruction_id = request.GET.get('instruction_id')
            gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
            library = Library.objects.filter(gp_practice=gp_practice).filter(key=word).first()

            instruction = Instruction.objects.get(pk=instruction_id)
            library_history = LibraryHistory(instruction=instruction, action='ReplaceAll', old=word, new=library.value)
            library_history.save()
            return JsonResponse({'replace_word': library.value, 'id': library_history.id})
        except:
            return JsonResponse({'message': 'Error'})


@login_required(login_url='/accounts/login')
def undo_last(request):
    if request.is_ajax():
        try:
            instruction_id = request.GET.get('instruction_id')
            instruction = Instruction.objects.get(pk=instruction_id)
            recent_history = LibraryHistory.objects.filter(instruction=instruction).last()

            highlight_html = '''
                <span class="highlight-library">
                    <span class="bg-warning">{}</span>
                    <span class="dropdown-options" data-xpath="{}">
                        <a href="#" class="highlight-redact">Redact</a>
                        <a href="javascript:;" class="highlight-replace">Replace</a>
                        <a href="#" class="highlight-replaceall">Replace all</a>
                    </span>
                </span>
            '''.format(recent_history.old, recent_history.xpath)

            gp_org = instruction.gp_user.organisation
            library_object = Library.objects.filter(gp_practice=gp_org, key=recent_history.old)
            for library in library_object:
                if not library.value:
                    highlight_html = '''
                        <span class="highlight-library">
                            <span class="bg-warning">{}</span>
                            <span class="dropdown-options" data-xpath="{}">
                                <a href="#" class="highlight-redact">Redact</a>
                            </span>
                        </span>
                    '''.format(recent_history.old, recent_history.xpath)

            data = {
                'action': recent_history.action,
                'old': recent_history.old,
                'new': recent_history.new,
                'text': highlight_html,
                'xpath': recent_history.xpath,
                'key': recent_history.key
            }
            recent_history.hard_delete()
            return JsonResponse(data)
        except:
            return JsonResponse({'message': 'Error'})


@login_required(login_url='/accounts/login')
def undo_all(request):
    if request.is_ajax():
        try:
            instruction_id = request.GET.get('instruction_id')
            instruction = Instruction.objects.get(pk=instruction_id)
            recent_history = LibraryHistory.objects.filter(instruction=instruction).order_by('-id')
            xpath_exist_list = list()                

            data = dict()
            data_list = list()

            for history in recent_history:
                if history.xpath not in xpath_exist_list:
                    highlight_html = str()
                    data_dict = dict()
                    if history.action not in ['mRedact', 'rmRedact',]:
                        highlight_html = '''
                            <span class="highlight-library">
                                <span class="bg-warning">{}</span>
                                <span class="dropdown-options" data-xpath="{}">
                                    <a href="#" class="highlight-redact">Redact</a>
                                    <a href="javascript:;" class="highlight-replace">Replace</a>
                                    <a href="#" class="highlight-replaceall">Replace all</a>
                                </span>
                            </span>
                        '''.format(history.old, history.xpath)

                        gp_org = instruction.gp_user.organisation
                        library_object = Library.objects.filter(gp_practice=gp_org, key=history.old)
                        for library in library_object:
                            if not library.value:
                                highlight_html = '''
                                    <span class="highlight-library">
                                        <span class="bg-warning">{}</span>
                                        <span class="dropdown-options" data-xpath="{}">
                                            <a href="#" class="highlight-redact">Redact</a>
                                        </span>
                                    </span>
                                '''.format(history.old, history.xpath)

                    data_dict['action'] = history.action
                    data_dict['old'] = history.old
                    data_dict['new'] = history.new
                    data_dict['text'] = highlight_html
                    data_dict['xpath'] = history.xpath
                    data_dict['key'] = history.key

                    xpath_exist_list.append(history.xpath)
                    data_list.append(data_dict)
                    history.hard_delete()
                else:
                    continue

            data['history'] = data_list
            return JsonResponse(data)
        except:
            return JsonResponse({'message': 'Error'})


@login_required(login_url='/accounts/login')
def manual_redact(request):
    if request.is_ajax():
        try:
            instruction_id = request.GET.get('instruction_id')
            xpath = request.GET.get('xpath')
            key = request.GET.get('key')
            action = 'mRedact'
            instruction = Instruction.objects.get(pk=instruction_id)

            last_action = LibraryHistory.objects.filter(
                action__in=['mRedact', 'rmRedact'],
                instruction= instruction,
                xpath= xpath,
            ).last()

            if last_action:
                if last_action.action == 'mRedact':
                    action = 'rmRedact'

            library_history = LibraryHistory(
                instruction= instruction,
                action= action,
                old= '',
                new= '',
                change_info= '',
                xpath= xpath,
                key= key
            )
            library_history.save()
            return JsonResponse({'message': 'Complete'})
        except:
            return JsonResponse({'message': 'Error'})