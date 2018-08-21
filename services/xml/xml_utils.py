import xml.etree.ElementTree as ET
import re


def xml_parse(xml_data):
    if type(xml_data) is ET.Element:
        return xml_data
    else:
        # Remove the default namespace definition (xmlns="http://some/namespace")
        xml_data = re.sub('\\sxmlns="[^"]+"', '', xml_data, count=1)
        parsed_xml = ET.fromstring(xml_data)
        return parsed_xml
