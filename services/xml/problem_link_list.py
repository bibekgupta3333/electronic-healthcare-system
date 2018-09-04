from .xml_base import XMLModelBase


class ProblemLinkList(XMLModelBase):
    XPATH = './/*[ProblemLinkList]'

    def target_guids(self):
        elements = self.parsed_xml.findall('ProblemLinkList/Link/Target/GUID')
        result_list = [element.text for element in elements]
        return result_list

    def date(self):
        return self.parsed_xml.find('AssignedDate').text if self.parsed_xml.find('AssignedDate') is not None else None

    def xpaths(self):
        xpaths = self.__parent_xpath() + self.__problem_xpath()
        return list(set(xpaths))

    # private
    def __parent_xpath(self):
        parent = self.parsed_xml.getparent().getparent().getparent()
        if parent is not None:
            xpath = ".//{}[GUID='{}']".format(parent.tag, parent.find('GUID').text)
            return [xpath]
        else:
            return []

    def __problem_xpath(self):
        return super().xpaths()
