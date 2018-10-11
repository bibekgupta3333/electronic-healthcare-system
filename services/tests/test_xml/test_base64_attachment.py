from django.test import TestCase
from django.test import tag
from services.xml.base64_attachment import Base64Attachment


@tag('notimplemented')
class Base64AttachmentTest(TestCase):
    def test_filedata(self):
        self.fail('Not implemented')

    def test_data(self):
        self.fail('Not implemented')

    def test_filename(self):
        self.fail('Not implemented')

    def test_file_basename(self):
        self.fail('Not implemented')
