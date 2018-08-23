from .xml_base import XMLModelBase
import yaml
import os
from django.conf import settings


class ValueEvent(XMLModelBase):
    XPATH = ".//Event[EventType='5']"
    SPECIFIED_BLOOD_CODES = None

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
        blood_snomed_concept_ids = self.SPECIFIED_BLOOD_CODES.get(type).get('snomed_concept_ids')
        blood_read_codes = self.SPECIFIED_BLOOD_CODES.get(type).get('read_codes')
        read_codes = self.readcodes()
        snomed_concepts = self.snomed_concepts()

        if read_codes:
            for code in blood_read_codes:
                if code in read_codes:
                    return True
        elif snomed_concepts:
            for code in blood_snomed_concept_ids:
                if code in snomed_concepts:
                    return True
        return False

    @classmethod
    def blood_test_types(cls):
        return cls.SPECIFIED_BLOOD_CODES.keys()


def load_bloods_data():
        filepath = os.path.join(settings.CONFIG_DIR, 'data/bloods.yml')
        with open(filepath, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)


if ValueEvent.SPECIFIED_BLOOD_CODES is None:
    ValueEvent.SPECIFIED_BLOOD_CODES = load_bloods_data()
