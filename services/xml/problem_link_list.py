from .xml_base import XMLModelBase


class ProblemLinkList(XMLModelBase):
    XPATH = './/*[ProblemLinkList]'

    def target_guids(self):
        elements = self.parsed_xml.findall('ProblemLinkList/Link/Target/GUID')
        result_list = [element.text for element in elements]
        return result_list

    def date(self):
        return self.parsed_xml.find('AssignedDate').text if self.parsed_xml.find('AssignedDate') is not None else None

    # def xpaths(self):
    #   [parent_xpath, problem_xpath].uniq
    # end

    # private

    # def __parent_xpath(self):
    #   XpathUtils.new.xpath_for(parsed_xml, depth_from_root: 3)
    # end

    # def __problem_xpath(self):
    #   XpathUtils.new.xpath_for(parsed_xml)
    # end
