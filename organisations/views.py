from django.shortcuts import render


def create_organisation(request):
    header_title = 'Add New Organisation'
    return render(request, 'organisations/create_organisation.html', {
        'header_title': header_title,
    })
