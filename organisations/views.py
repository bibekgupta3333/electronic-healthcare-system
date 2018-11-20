from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from organisations.models import OrganisationGeneralPractice


def create_organisation(request):
    header_title = 'Add New Organisation'
    return render(request, 'organisations/create_organisation.html', {
        'header_title': header_title,
    })


def get_gporganisation_data(request, **kwargs):
    code = request.GET.get('code', '')
    data = {
        'name': '',
        'address': '',
    }
    if code:
        gp_organisation = OrganisationGeneralPractice.objects.filter(practcode=code).first()
        if gp_organisation:
            data = {
                'name': gp_organisation.name,
                'address': ' '.join(
                    (
                        gp_organisation.region,
                        gp_organisation.comm_area,
                        gp_organisation.billing_address_street,
                        gp_organisation.billing_address_city,
                        gp_organisation.billing_address_state,
                        gp_organisation.billing_address_postalcode,
                    )
                )
            }

    if kwargs.get('need_dict'):
        return data

    return JsonResponse(data)


def get_nhs_autocomplete(request):
    data = {
        'items': [
            {
                'text': 'GP Organisations',
                'children': []
            },
            {
                'text': 'NHS Organisations',
                'children': []
            }
        ]
    }
    search = request.GET.get('search', '')
    if search:
        organisation_gps = OrganisationGeneralPractice.objects.filter(live=True, accept_policy=True).filter(name__icontains=search)
        nhs_gps = OrganisationGeneralPractice.objects.filter(Q(live=False) | Q(accept_policy=False)).filter(name__icontains=search)
    else:
        organisation_gps = OrganisationGeneralPractice.objects.filter(live=True, accept_policy=True).all()[:10]
        nhs_gps = OrganisationGeneralPractice.objects.filter(Q(live=False) | Q(accept_policy=False)).filter(name__icontains=search)[:10]

    if organisation_gps.exists():
        for organisation_gp in organisation_gps:
            data['items'][0]['children'].append(
                {'id': organisation_gp.practcode, 'text': organisation_gp.name})

    if nhs_gps.exists():
        for nhs_gp in nhs_gps:
            data['items'][1]['children'].append({'id': nhs_gp.practcode, 'text': nhs_gp.name})

    return JsonResponse(data)


def get_sign_up_autocomplete(request):
    data = {
        'items': []
    }
    name = request.GET.get('name', '')
    code = request.GET.get('code', '')
    filter_conditions = Q(live=False) | Q(accept_policy=False)
    if name:
        nhs_gps = OrganisationGeneralPractice.objects.filter(filter_conditions).filter(name__icontains=name)
    elif code:
        nhs_gps = OrganisationGeneralPractice.objects.filter(filter_conditions).filter(practcode__icontains=code)
    else:
        nhs_gps = OrganisationGeneralPractice.objects.filter(filter_conditions).all()[:10]

    for nhs_gp in nhs_gps:
        if name:
            data['items'].append({'id': nhs_gp.practcode, 'text': nhs_gp.name})
        elif code:
            data['items'].append({'id': nhs_gp.practcode, 'text': nhs_gp.practcode})

    return JsonResponse(data)


def get_gp_sign_up_data(request, **kwargs):
    code = request.GET.get('code', '')
    name = request.GET.get('name', '')
    data = {
        'code': '',
        'name': '',
        'street': '',
        'city': '',
        'postcode': '',
        'phone_office': '',
    }
    if code:
        gp_organisation = OrganisationGeneralPractice.objects.filter(practcode=code).first()
        if not gp_organisation and name:
            gp_organisation = OrganisationGeneralPractice.objects.filter(name=name).first()
        if gp_organisation:
            data = {
                'code': gp_organisation.practcode,
                'name': gp_organisation.name,
                'street': gp_organisation.billing_address_street,
                'city': gp_organisation.billing_address_city,
                'postcode': gp_organisation.billing_address_postalcode,
                'phone_office': gp_organisation.phone_office,
            }

    if kwargs.get('need_dict'):
        return data

    return JsonResponse(data)
