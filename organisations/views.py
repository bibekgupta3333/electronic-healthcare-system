from django.shortcuts import render
from django.http import JsonResponse

from organisations.models import NHSgpPractice


def create_organisation(request):
    header_title = 'Add New Organisation'
    return render(request, 'organisations/create_organisation.html', {
        'header_title': header_title,
    })


def get_nhs_data(request):
    nhs_code = request.GET.get('nhs_code', '')
    if nhs_code:
        nhs_gp = NHSgpPractice.objects.filter(code=nhs_code).first()

        data = {
            'name': nhs_gp.name,
            'address_line1': nhs_gp.address_line1,
            'address_line2': nhs_gp.address_line2,
            'address_line3': nhs_gp.address_line3,
            'country': nhs_gp.country,
            'post_code': nhs_gp.post_code
        }

    return JsonResponse(data)


def get_nhs_autocomplete(request):
    data = {'items': []}
    search = request.GET.get('search', '')
    if search:
        nhs_gps = NHSgpPractice.objects.filter(name__icontains=search)
        if nhs_gps.exists():
            for nhs_gp in nhs_gps:
                data['items'].append({'id': nhs_gp.code, 'text':nhs_gp.name})
    return JsonResponse(data)