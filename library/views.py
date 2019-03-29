from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
from django.db.models import Q

from instructions.views import calculate_next_prev

from .models import Library
from .tables import LibraryTable


@login_required(login_url='/accounts/login')
def edit_library(request):
    header_title = "Surgery Library"
    page_length = 10
    search_input = ''
    gp_practice = request.user.userprofilebase.generalpracticeuser.organisation
    library = Library.objects.filter(gp_practice=gp_practice)

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
        'search_input': search_input
    })