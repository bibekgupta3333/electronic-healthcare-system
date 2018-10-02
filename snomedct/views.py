from django.http import JsonResponse
from .models import SnomedConcept
from django.db.models import Q

QUERY_METHOD = ['istartswith', 'iendswith', 'icontains']


# Create your views here.
def query_snomed(request):
    query = request.GET.get('keyword')
    method = request.GET.get('method', 'icontains')

    if method not in QUERY_METHOD:
        raise ValueError("query method is not supported {}".format(method))

    if query:
        kwargs = {
            '{0}__{1}'.format('fsn_description', method): query,
        }
        results = SnomedConcept.objects.filter(Q(fsn_description__icontains=query) & Q(fsn_description__icontains='(disorder)'))
    else:
        results = SnomedConcept.objects.filter(fsn_description__icontains='(disorder)')[:100]

    response = []
    for item in results:
        response.append({
            "id": item.external_id,
            "text": item.fsn_description,
        })
    return JsonResponse(response, safe=False)


def get_descendants(request):
    external_id = request.GET.get('snomedct')
    if external_id:
        record = SnomedConcept.objects.get(external_id=external_id)
        snomed_descendants = record.snomed_descendants()

    response = []
    for item in snomed_descendants:
        response.append({
            "id": item.id,
            "fsn_description": item.fsn_description,
            "external_id": item.external_id
        })
    return JsonResponse(response, safe=False)


def get_descendant_readcodes(request):
    external_id = request.GET.get('snomedct')
    if external_id:
        record = SnomedConcept.objects.get(external_id=external_id)
        readcodes = record.snomed_descendant_readcodes()

    response = []
    for item in readcodes:
        response.append({
            "id": item.id,
            "ext_read_code": item.ext_read_code,
            "fsn_description": item.concept_id.fsn_description,
            "external_id": item.concept_id.external_id
        })
    return JsonResponse(response, safe=False)


def get_readcodes(request):
    external_id = request.GET.get('snomedct')
    if external_id:
        record = SnomedConcept.objects.get(external_id=external_id)
        readcodes = record.readcodes()

    response = []
    for item in readcodes:
        response.append({
            "id": item.id,
            "ext_read_code": item.ext_read_code,
            "fsn_description": item.concept_id.fsn_description,
            "external_id": item.concept_id.external_id
        })
    return JsonResponse(response, safe=False)
