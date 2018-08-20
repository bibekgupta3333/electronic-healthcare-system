import datetime
from .xml_base import XMLBase


class Registration(XMLBase):
    XPATH = './/Registration'
    NAME_XPATHS = ['Title', 'FirstNames', 'FamilyName']
    ADDRESS_XPATHS = ['HouseNameFlat', 'Street', 'Village', 'Town', 'County', 'PostCode']

    def date_of_birth(self):
        return self.parsed_xml.find('DateOfBirth').text

    def parsed_date_of_birth(self):
        parsed_date = None
        date_of_birth = self.date_of_birth()
        if date_of_birth:
            parsed_date = datetime.datetime.strptime(date_of_birth, "%d/%m/%Y")
        return parsed_date

    def sex(self):
        return self.parsed_xml.find('Sex').text

    def full_name(self):
        name = []
        for xpath in self.NAME_XPATHS:
            value = self.parsed_xml.find(xpath).text
            if value is not None:
                name.append(value)
        return ' '.join(name)

    def nhs_number(self):
        return self.parsed_xml.find('NhsNumber').text

    def address_lines(self):
        address = []
        for xpath in self.ADDRESS_XPATHS:
            value = self.parsed_xml.find('Address/{}'.format(xpath)).text
            if value is not None:
                address.append(value)
        return address

    def ref_id(self):
        return self.parsed_xml.find('RefID').text
