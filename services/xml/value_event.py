from .xml_base import XMLModelBase
import yaml
import os
from django.conf import settings


class ValueEvent(XMLModelBase):
    XPATH = ".//Event[EventType='5']"
    SPECIFIED_BLOOD_CODES = None

    def __load_bloods_data(self):
        filepath = os.path.join(settings.CONFIG_DIR, 'data/bloods.yml')
        with open(filepath, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def __init__(self, xml_data):
        super().__init__(xml_data)
        if not ValueEvent.SPECIFIED_BLOOD_CODES:
            ValueEvent.SPECIFIED_BLOOD_CODES = self.__load_bloods_data()

    def __str__(self):
        return "ValueEvent"

    def date(self):
        return self.parsed_xml.find('AssignedDate').text

    def description(self):
        value = self.parsed_xml.find('NumericValue/Value').text
        unit = self.parsed_xml.find('NumericValue/Units').text
        return "{} {}".format(value, unit)

    def has_bmi(self):
        # readcodes.any? ? readcodes.include?('22K..') : snomed_concepts.include?('60621009')
        readcodes = self.readcodes()
        if readcodes:
            if '22K..' in readcodes:
                return True
            else:
                return False
        else:
            if '60621009' in self.snomed_concepts():
                return True
            else:
                return False

    def has_weight(self):
        readcodes = self.readcodes()
        if readcodes:
            if '22A..' in readcodes:
                return True
            else:
                return False
        else:
            if '162763007' in self.snomed_concepts():
                return True
            else:
                return False

    def has_height(self):
        readcodes = self.readcodes()
        if readcodes:
            if '229..' in readcodes:
                return True
            else:
                return False
        else:
            if '162755006' in self.snomed_concepts():
                return True
            else:
                return False

    def has_systolic_blood_pressure(self):
        readcodes = self.readcodes()
        if readcodes:
            if '2469.' in readcodes:
                return True
            else:
                return False
        else:
            if '163030003' in self.snomed_concepts():
                return True
            else:
                return False

    def has_diastolic_blood_pressure(self):
        readcodes = self.readcodes()
        if readcodes:
            if '246A.' in readcodes:
                return True
            else:
                return False
        else:
            if '163031004' in self.snomed_concepts():
                return True
            else:
                return False

    def has_blood_test(self, type):
        return "not implement"
        # blood_snomed_concept_ids = self.SPECIFIED_BLOOD_CODES.get(type).get('snomed_concept_ids')
        # blood_read_codes = self.SPECIFIED_BLOOD_CODES.get(type).get('read_codes')
        # if self.readcodes():
        #     print(blood_read_codes)
        #     # blood_read_codes.any? { |readcode| readcode.in?(readcodes) }
        # else:
        #     print(blood_snomed_concept_ids)
        #     blood_snomed_concept_ids.any? { |snomed| snomed.in?(snomed_concepts) }

    # def blood_test_types(self):
    #     return self.SPECIFIED_BLOOD_CODES.keys()
