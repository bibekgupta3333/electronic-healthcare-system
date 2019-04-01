from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_tables2 import RequestConfig
from django.db.models import Q

from instructions.views import calculate_next_prev

from .models import Library
from .tables import LibraryTable
from .forms import LibraryForm


@login_required(login_url='/accounts/login')
def edit_library(request, event):
    header_title = "Surgery Library"
    page_length = 10
    search_input = ''
    gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
    library = Library.objects.filter(gp_practice=gp_practice)
    library_form = LibraryForm()
    duplicate_error_message = ''
    if request.method == 'POST':
        library_form = LibraryForm(request.POST)
        if library_form.is_valid():
            library_obj = library_form.save(commit=False)
            library_obj.gp_practice = gp_practice
            library_obj.save()
            library_form = LibraryForm()
            messages.success(request, 'Add word successfully')
        else:
            duplicate_error_message = 'This word already exist in your library. If you wish to edit it, please go back' \
                                      'to the library and edit from there'

    if 'page_length' in request.GET:
        page_length = int(request.GET.get('page_length'))

    if 'search' in request.GET:
        search_input = request.GET.get('search')
        library = library.filter(Q(key__icontains=search_input) | Q(value__icontains=search_input))

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
        'duplicate_error_message': duplicate_error_message,
    })


@login_required(login_url='/accounts/login')
def delete_library(request, library_id):
    library = get_object_or_404(Library, pk=library_id)
    library.hard_delete()

    return redirect('library:edit_library', event='delete')
