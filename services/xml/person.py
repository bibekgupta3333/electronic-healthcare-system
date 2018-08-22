from .xml_base import XMLBase


class Person(XMLBase):
    XPATH = './/Person'

    NAME_XPATHS = ['FirstNames', 'LastName']

    def full_name(self):
        result = self.name()
        if self.category_description() is not '':
            result = '{} ({})'.format(result, self.category_description())
        return result

    def category_description(self):
        return self.parsed_xml.find('Category/Description').text if self.parsed_xml.find('Category/Description') is not None else ''

    def name(self):
        result = []
        for xpath in self.NAME_XPATHS:
            value = self.parsed_xml.find(xpath).text if self.parsed_xml.find(xpath) is not None else None
            if value is not None:
                result.append(value)

        return ' '.join(result)

    def ref_id(self):
        return self.parsed_xml.find('RefID').text if self.parsed_xml.find('RefID') is not None else None
