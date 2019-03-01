from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from django.template import loader
from django.core.mail import send_mail

from services.xml.base64_attachment import Base64Attachment
from medicalreport.models import AmendmentsForRecord
from services.xml.medical_report_decorator import MedicalReportDecorator
from services.emisapiservices import services
from instructions.models import Instruction
from instructions.model_choices import INSTRUCTION_STATUS_COMPLETE
from report.mobile import SendSMS
from silk.profiling.profiler import silk_profile

from celery import shared_task
from PIL import Image
import PyPDF2
import subprocess
import img2pdf
import reportlab
import reportlab.lib.pagesizes as pdf_sizes
import logging
import io
import uuid
import glob
import os

logger = logging.getLogger(__name__)
time_logger = logging.getLogger('timestamp')


def send_patient_mail(scheme, host,  unique_url, instruction):
    report_link = scheme + '://' + host + '/report/' + str(instruction.pk) + '/patient/' + unique_url
    send_mail(
        'Notification from your GP surgery',
        '',
        'MediData',
        [instruction.patient_information.patient_email],
        fail_silently=True,
        html_message=loader.render_to_string('medicalreport/patient_email.html', {
            'surgery_name': instruction.gp_practice,
            'report_link': report_link
        })
    )


@shared_task(bind=True)
@silk_profile(name='Create Patient')
def generate_medicalreport_with_attachment(self, instruction_id, report_link_info):
    start_time = timezone.now()

    try:
        instruction = get_object_or_404(Instruction, id=instruction_id)
        redaction = get_object_or_404(AmendmentsForRecord, instruction=instruction_id)

        medical_record_decorator = MedicalReportDecorator(instruction.medical_xml_report.read().decode('utf-8'),
                                                          instruction)
        output = PyPDF2.PdfFileWriter()

        # add each page of medical report to output file
        medical_report = PyPDF2.PdfFileReader(instruction.medical_report)
        for page_num in range(medical_report.getNumPages()):
            output.addPage(medical_report.getPage(page_num))

        # create list of PdfFileReader obj from raw bytes of xml data
        attachments_pdf = []
        unique_file_name = []
        folder = settings.BASE_DIR + '/static/generic_pdf/'
        for attachment in medical_record_decorator.attachments():
            unique = uuid.uuid4().hex
            unique_file_name.append(unique)
            xpaths = attachment.xpaths()
            if redaction.redacted(xpaths) is not True:
                raw_xml_or_status_code = services.GetAttachment(
                    instruction.patient_information.patient_emis_number,
                    attachment.dds_identifier(),
                    gp_organisation=instruction.gp_practice).call()

                file_name = Base64Attachment(raw_xml_or_status_code).filename()
                file_type = file_name.split('.')[-1]
                raw_attachment = Base64Attachment(raw_xml_or_status_code).data()
                buffer = io.BytesIO(raw_attachment)
                try:
                    if file_type == 'pdf':
                        attachments_pdf.append(PyPDF2.PdfFileReader(buffer))
                    elif file_type in ['doc', 'docx', 'rtf']:
                        tmp_file = 'temp_%s.' % unique + file_type
                        f = open(folder + tmp_file, 'wb')
                        f.write(buffer.getvalue())
                        f.close()
                        subprocess.call(
                            ("export HOME=/tmp && libreoffice --headless --convert-to pdf --outdir " + folder + " " + folder + "/" + tmp_file),
                            shell=True
                        )
                        pdf = open(folder + 'temp_%s.pdf' % unique, 'rb')
                        attachments_pdf.append(PyPDF2.PdfFileReader(pdf))
                    elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'tif']:
                        image = Image.open(buffer)
                        image_format = image.format
                        if image_format == "TIFF":
                            max_pages = 200
                            height = image.tag[0x101][0]
                            width = image.tag[0x100][0]
                            out_pdf_io = io.BytesIO()
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
                            attachments_pdf.append(PyPDF2.PdfFileReader(out_pdf_io))
                        else:
                            pdf_bytes = img2pdf.convert('img_temp_%s.pdf' % unique)
                            f = open(folder + 'img_temp_%s.pdf' % unique, 'wb')
                            f.write(pdf_bytes)
                            attachments_pdf.append(PyPDF2.PdfFileReader(f))
                            image.close()
                            f.close()
                except Exception as e:
                    logger.error(e)

        # add each page of each attachment to output file
        for pdf in attachments_pdf:
            if pdf.isEncrypted:
                pdf.decrypt(password='')
            for page_num in range(pdf.getNumPages()):
                output.addPage(pdf.getPage(page_num))

        pdf_page_buf = io.BytesIO()
        output.write(pdf_page_buf)

        uuid_hex = uuid.uuid4().hex
        instruction.medical_with_attachment_report.save('report_with_attachments_%s.pdf' % uuid_hex,
                                                        ContentFile(pdf_page_buf.getvalue()))

        # remove temp files
        for unique in unique_file_name:
            for file_path in glob.glob(folder+'*{unique}*'.format(unique=unique)):
                os.remove(file_path)
    except Exception as e:
        # waiting for 5 min to retry
        raise self.retry(countdown=60*5, exc=e, max_retires=2)

    if instruction.medical_with_attachment_report:
        SendSMS(number=instruction.patient_information.get_telephone_e164()).send()
        send_patient_mail(
            report_link_info['scheme'],
            report_link_info['host'],
            report_link_info['unique_url'],
            instruction
        )

        instruction.status = INSTRUCTION_STATUS_COMPLETE
        instruction.save()

    end_time = timezone.now()
    total_time = end_time - start_time
    time_logger.info(
        "[PROCESS ATTACHMENTS] %s seconds with patient %s" % (
            total_time.seconds, instruction.patient_information.__str__()
        )
    )
