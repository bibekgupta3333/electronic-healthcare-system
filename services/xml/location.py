from .xml_base import XMLBase


class Location(XMLBase):
    ADDRESS_XPATHS = ['HouseNameFlat', 'Street', 'Village', 'Town', 'County', 'PostCode']
    XPATH = './/Location'

    def address_lines(self):
        address_values = []
        for xpath in self.ADDRESS_XPATHS:
            value = self.parsed_xml.find("Address/{}".format(xpath)).text if self.parsed_xml.find("Address/{}".format(xpath)) is not None else None
            if value is not None:
                address_values.append(value)

        location_name = [self.location_name()]
        return location_name + address_values

    def location_name(self):
        return self.parsed_xml.find('LocationName').text if self.parsed_xml.find('LocationName') is not None else None

    def ref_id(self):
        return self.parsed_xml.find('RefID').text if self.parsed_xml.find('RefID') is not None else None
