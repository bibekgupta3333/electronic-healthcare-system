import os
import xhtml2pdf.pisa as pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from django.conf import settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = BASE_DIR + '/medicalreport/templates/medicalreport/reports/medicalreport.html'


def link_callback(uri, rel):
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT

    if uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))

    path = BASE_DIR + '/medi/' + path

    if not os.path.isfile(path):
        raise Exception('static URI must start with %s' % (sUrl))
    return path


class MedicalReport:

    @staticmethod
    def render(params: dict):
        template = get_template(REPORT_DIR)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response, link_callback=link_callback)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

    @staticmethod
    def download(params: dict):
        template = get_template(REPORT_DIR)
        html = template.render(params)
        file = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), file, link_callback=link_callback)

        if not pdf.err:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            response.write(file.getvalue())
            return response
