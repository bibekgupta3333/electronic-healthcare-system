from .xml_base import XMLModelBase
import datetime


class Problem(XMLModelBase):
    XPATH = './/*[Problem]'

    def is_active(self):
        value = self.parsed_xml.find('Problem/ProblemStatus').text if self.parsed_xml.find('Problem/ProblemStatus') is not None else None
        return value == '1'

    def is_past(self):
        value = self.parsed_xml.find('Problem/ProblemStatus').text if self.parsed_xml.find('Problem/ProblemStatus') is not None else None
        return value == '0'

    def is_significant(self):
        value = self.parsed_xml.find('Problem/Significance').text if self.parsed_xml.find('Problem/Significance') is not None else None
        return value == '1'

    def date(self):
        return self.parsed_xml.find('AssignedDate').text if self.parsed_xml.find('AssignedDate') is not None else None

    def end_date(self):
        if not self.is_active():
            return self.parsed_xml.find('Problem/EndDate').text if self.parsed_xml.find('Problem/EndDate') is not None else None
        else:
            return None

    def parsed_end_date(self):
        end_date = self.end_date()
        if end_date is not None:
            return datetime.datetime.strptime(end_date, "%d/%m/%Y")
        else:
            return None

    def description(self):
        display_term = self.parsed_xml.find('DisplayTerm').text if self.parsed_xml.find('DisplayTerm') is not None else None
        if display_term is not None:
            description = display_term
        else:
            description = self.parsed_xml.find('Code/Term').text if self.parsed_xml.find('Code/Term') is not None else None
        return description

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
