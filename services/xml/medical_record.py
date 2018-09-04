from .registration import Registration
from .consultation import Consultation
from .medication import Medication
from .allergy_event import AllergyEvent
from .allergy import Allergy
from .value_event import ValueEvent
from .problem import Problem
from .referral import Referral
from .referral_event import ReferralEvent
from .attachment import Attachment
from .person import Person
from .location import Location
from .problem_link_list import ProblemLinkList
from .social_consultation_element import SocialConsultationElement
from .xml_base import XMLBase


class MedicalRecord(XMLBase):
    XPATH = './/MedicalRecord'
    PROFILE_EVENT_TYPES = ['height', 'weight', 'bmi', 'smoking', 'alcohol', 'systolic_blood_pressure', 'diastolic_blood_pressure']

    def consultations(self):
        elements = self.parsed_xml.findall(Consultation.XPATH)
        result_list = [Consultation(element) for element in elements]
        return result_list

    def registration(self):
        return Registration(self.parsed_xml.find(Registration.XPATH))

    def acute_medications(self):
        medications = self.__medications()
        result_list = []
        for medication in medications:
            if medication.is_acute():
                result_list.append(medication)
        return result_list

    def repeat_medications(self):
        medications = self.__medications()
        result_list = []
        for medication in medications:
            if medication.is_repeat():
                result_list.append(medication)
        return result_list

    def referrals(self):
        referral_items = self.__referral_items()
        referral_event_items = self.__referral_event_items()
        return referral_items + referral_event_items

    def attachments(self):
        elements = self.parsed_xml.findall(Attachment.XPATH)
        result_list = [Attachment(element) for element in elements]
        return result_list

    def all_allergies(self):
        allergies_list = self.__allergies()
        event_allergies = self.__event_allergies()
        return allergies_list + event_allergies

    def people(self):
        elements = self.parsed_xml.findall(Person.XPATH)
        result_list = [Person(element) for element in elements]
        return result_list

    def locations(self):
        elements = self.parsed_xml.findall(Location.XPATH)
        result_list = [Location(element) for element in elements]
        return result_list

    def problem_linked_lists(self):
        elements = self.parsed_xml.findall(ProblemLinkList.XPATH)
        result_list = [ProblemLinkList(element) for element in elements]
        return result_list

    def height(self):
        result_list = []
        value_events = self.__value_events()
        for event in value_events:
            if event.has_height():
                result_list.append(event)
        return result_list

    def weight(self):
        result_list = []
        value_events = self.__value_events()
        for event in value_events:
            if event.has_weight():
                result_list.append(event)
        return result_list

    def bmi(self):
        result_list = []
        value_events = self.__value_events()
        for event in value_events:
            if event.has_bmi():
                result_list.append(event)
        return result_list

    def systolic_blood_pressure(self):
        result_list = []
        value_events = self.__value_events()
        for event in value_events:
            if event.has_systolic_blood_pressure():
                result_list.append(event)
        return result_list

    def diastolic_blood_pressure(self):
        result_list = []
        value_events = self.__value_events()
        for event in value_events:
            if event.has_diastolic_blood_pressure():
                result_list.append(event)
        return result_list

    def blood_test(self, type):
        result_list = []
        value_events = self.__value_events()
        for event in value_events:
            if event.has_blood_test(type):
                result_list.append(event)
        return result_list

    def test(self):
        # for t in self.PROFILE_EVENT_TYPES:
        #     self.profile_event(t)
        for item in ValueEvent.blood_test_types():
            self.blood_test(item)

    def profile_event(self, type):
        if type in self.PROFILE_EVENT_TYPES:
            function = getattr(self, type)
            return function()
        return []

    def smoking(self):
        # social_consultation_elements.select(&:smoking?)
        return []

    def alcohol(self):
        # social_consultation_elements.select(&:alcohol?)
        return []

    def significant_active_problems(self):
        result_list = []
        significant_problems = self.__significant_problems()
        for problem in significant_problems:
            if problem.is_active():
                result_list.append(problem)
        return result_list

    def significant_past_problems(self):
        result_list = []
        significant_problems = self.__significant_problems()
        for problem in significant_problems:
            if problem.is_past():
                result_list.append(problem)
        return result_list

    # @classmethod
    # def profile_event_types(cls):
    #     return [cls.height(), cls.weight(), cls.bmi(), cls.smoking(), cls.alcohol(),
    #             cls.systolic_blood_pressure(), cls.diastolic_blood_pressure()]

    # private method
    def __event_allergies(self):
        elements = self.parsed_xml.findall(AllergyEvent.XPATH)
        result_list = [AllergyEvent(element) for element in elements]
        return result_list

    def __allergies(self):
        elements = self.parsed_xml.findall(Allergy.XPATH)
        result_list = [Allergy(element) for element in elements]
        return result_list

    def __medications(self):
        elements = self.parsed_xml.findall(Medication.XPATH)
        result_list = [Medication(element) for element in elements]
        return result_list

    def __value_events(self):
        elements = self.parsed_xml.findall(ValueEvent.XPATH)
        result_list = [ValueEvent(element) for element in elements]
        return result_list

    def __social_consultation_elements(self):
        elements = self.parsed_xml.xpath(SocialConsultationElement.XPATH)
        result_list = [SocialConsultationElement(element) for element in elements]
        return result_list

    def __significant_problems(self):
        elements = self.parsed_xml.xpath(Problem.XPATH)
        problem_list = [Problem(element) for element in elements]
        return list(filter(lambda problem: problem.is_significant() is True, problem_list))

    def __referral_items(self):
        elements = self.parsed_xml.findall(Referral.XPATH)
        result_list = [Referral(element) for element in elements]
        return result_list

    def __referral_event_items(self):
        elements = self.parsed_xml.findall(ReferralEvent.XPATH)
        result_list = [ReferralEvent(element) for element in elements]
        return result_list
