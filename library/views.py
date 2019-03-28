from django.shortcuts import render


def edit_library(request):
    header_title = "Surgery Library"
    return render(request, 'library/edit_library.html', {
        'header_title': header_title
    })