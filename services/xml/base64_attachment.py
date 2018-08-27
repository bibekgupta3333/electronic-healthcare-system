from .xml_base import XMLBase
import base64
import re


class Base64Attachment(XMLBase):
    XPATH = './/Base64Attachment'

    def filedata(self):
        return self.parsed_xml.find('filedata').text if self.parsed_xml.find('filedata') is not None else None

    def data(self):
        file_data = self.filedata()
        if file_data is not None:
            return base64.b64decode(file_data)
        return None

    def filename(self):
        return self.parsed_xml.find('filename').text if self.parsed_xml.find('filename') is not None else None

    def file_basename(self):
        filename = self.filename()
        if filename is not None:
            return re.findall(r'[^\\]+\Z', filename)[0]
        return None
