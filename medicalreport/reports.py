import os
import logging
import re
import xhtml2pdf.pisa as pisa
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.template.loader import get_template
from services.xml.base64_attachment import Base64Attachment
from services.emisapiservices import services
import reportlab
from django.urls import reverse
import reportlab.lib.pagesizes as pdf_sizes
from PIL import Image
from django.conf import settings
#from silk.profiling.profiler import silk_profile
import subprocess


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = BASE_DIR + '/medicalreport/templates/medicalreport/reports/medicalreport.html'
TEMP_DIR = BASE_DIR + '/medi/static/generic_pdf/'
logger = logging.getLogger('timestamp')


def link_callback(uri, rel):
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT

    if uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        path = sRoot

    if sRoot == 'static':
        path = BASE_DIR + '/medi/' + path

    if not os.path.isfile(path):
        raise Exception('static URI must start with %s' % (sUrl))
    return path


class MedicalReport:

    @staticmethod
    def render(params: dict):
        start_time = timezone.now()
        template = get_template(REPORT_DIR)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response, link_callback=link_callback)
        end_time = timezone.now()
        total_time = end_time - start_time
        logger.info("[GENERATE PDF WITH XML] %s seconds with instruction %s"%(total_time.seconds, params.get('instruction')))
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

    @staticmethod
    #@silk_profile(name='Get PDF Medical Report Method')
    def get_pdf_file(params: dict):
        template = get_template(REPORT_DIR)
        html = template.render(params)
        file = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), file, link_callback=link_callback)
        if not pdf.err:
            return ContentFile(file.getvalue())


class AttachmentReport:
    def __init__(self, instruction: object, raw_xml: str, path_file: str):
        self.instruction = instruction
        self.path_file = path_file
        self.raw_xml = raw_xml
        self.file_name = Base64Attachment(self.raw_xml).filename()
        self.file_type = self.file_name.split('.')[-1]

    def render(self):
        if self.file_type == "pdf":
            return self.render_pdf()
        elif self.file_type in ["rtf", "doc", "docx"]:
            return self.render_pdf_with_libreoffice()
        elif self.file_type in ["jpg", "jpeg", "png", "tiff", "tif"]:
            return self.render_image()
        else:
            return self.render_download_file()

    def download(self):
        path_patient = self.instruction.patient_information.__str__()
        attachment = Base64Attachment(self.raw_xml).data()
        buffer = BytesIO()
        buffer.write(attachment)
        save_file = '%s_tmp_attachments.%s'%(self.instruction.pk, self.file_type)
        f = open(TEMP_DIR + save_file, 'wb')
        f.write(buffer.getvalue())
        f.close()
        download_file = open(TEMP_DIR + save_file, 'rb')
        response = HttpResponse(download_file, content_type="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename=' + self.file_name.split('\\')[-1]
        return response

    def render_download_file(self):
        link = reverse(
            'medicalreport:download_attachment',
            kwargs={'path_file': self.path_file, 'instruction_id': self.instruction.id}
        )
        return render_to_response('medicalreport/preview_and_download.html', {'link': link})

    def render_error(self):
        return render_to_response('errors/handle_errors_convert_file.html')

    def render_pdf(self):
        attachment = Base64Attachment(self.raw_xml).data()
        buffer = BytesIO()
        buffer.write(attachment)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/pdf",
        )
        return response

    def render_pdf_with_libreoffice(self):
        attachment = Base64Attachment(self.raw_xml).data()
        buffer = BytesIO()
        buffer.write(attachment)
        tmp_file = '%s_tmp.%s'%(self.instruction.pk, self.file_type)
        f = open(TEMP_DIR + tmp_file, 'wb')
        f.write(buffer.getvalue())
        f.close()
        subprocess.call(
            ("export HOME=/tmp && libreoffice --headless --convert-to pdf --outdir " + TEMP_DIR + " " + TEMP_DIR + tmp_file),
            shell=True
        )
        pdf = open(TEMP_DIR + '%s_tmp.pdf'%self.instruction.pk, 'rb')
        response = HttpResponse(
            pdf,
            content_type="application/pdf",
        )
        return response

    def render_image(self):
        attachment = Base64Attachment(self.raw_xml).data()
        image = Image.open(BytesIO(attachment))
        image_format = image.format
        if image_format == "TIFF":
            return self.render_pdf_with_tiff(image)
        extension = str(image_format)
        response = HttpResponse(content_type="image/" + extension.lower())
        image.save(response, image_format)
        return response

    def render_pdf_with_tiff(self, image, max_pages = 200):
        height = image.tag[0x101][0]
        width = image.tag[0x100][0]
        out_pdf_io = BytesIO()
        c = reportlab.pdfgen.canvas.Canvas(out_pdf_io, pagesize=pdf_sizes.letter)
        pdf_width, pdf_height = pdf_sizes.letter
        page = 0
        while True:
            try:
                image.seek(page)
            except EOFError:
                break
            if pdf_width * height / width <= pdf_height:
                c.drawInlineImage(image, 0, 0, pdf_width, pdf_width * height / width)
            else:
                c.drawInlineImage(image, 0, 0, pdf_height * width / height, pdf_height)
            c.showPage()
            if max_pages and page > max_pages:
              break
            page += 1
        c.save()
        response = HttpResponse(
            out_pdf_io.getvalue(),
            content_type="application/pdf",
        )
        return response
