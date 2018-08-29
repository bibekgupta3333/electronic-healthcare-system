from lxml import etree
import re


def xml_parse(xml_data):
    if etree.iselement(xml_data):
        return xml_data
    else:
        # Remove the default namespace definition (xmlns="http://some/namespace")
        xml_data = re.sub('\\sxmlns="[^"]+"', '', xml_data, count=1)
        parsed_xml = etree.fromstring(xml_data)
        return parsed_xml


def redaction_elements(xml_data, remove_xpaths):
    xml = xml_parse(xml_data)
    for xpath in remove_xpaths:
        element = xml.xpath(xpath)
        if element:
            e = element[0]
            e.getparent().remove(e)
    return xml
