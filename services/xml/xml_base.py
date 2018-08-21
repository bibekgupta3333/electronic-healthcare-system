from . import xml_utils


class XMLBase(object):
    def __init__(self, xml_data):
        self.parsed_xml = xml_utils.xml_parse(xml_data)
