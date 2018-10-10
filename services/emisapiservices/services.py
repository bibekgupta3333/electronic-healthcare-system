from django.conf import settings
import urllib
import requests
from ..models import EmisAPIConfig
from accounts.models import Patient


class EmisAPIServiceBase:
    def __init__(self):
        self.emis_api_config = EmisAPIConfig.objects.first()
        if self.emis_api_config is None:
            raise ValueError('Unable to get EMIS API Configuration')

    def uri(self) -> str:
        raise NotImplementedError(
            "Inheriting classes must implement this method."
        )

    def call(self) -> str:
        request_uri = self.uri()
        r = requests.get(
            request_uri,
            auth=(
                self.emis_api_config.emis_username,
                self.emis_api_config.emis_password
            )
        )
        r.raise_for_status()
        return r.text


class GetAttachment(EmisAPIServiceBase):
    def __init__(self, patient_number: str, attachment_identifier: str):
        super().__init__()
        self.patient_number = patient_number
        self.attachment_identifier = attachment_identifier

    def uri(self) -> str:
        uri = "{host}/api/organisations/{organisation_id}/patients/{patient_number}/attachments/{attachment_identifier}".format(
            host=settings.EMIS_API_HOST,
            organisation_id=self.emis_api_config.emis_organisation_id,
            patient_number=self.patient_number,
            attachment_identifier=urllib.parse.quote(self.attachment_identifier, safe=''))
        return uri


class GetPatientList(EmisAPIServiceBase):
    def __init__(self, patient: Patient):
        super().__init__()
        self.patient = patient

    def search_term(self) -> str:
        terms = [
            self.patient.user.first_name,
            self.patient.user.last_name,
        ]
        if self.patient.date_of_birth is not None:
            terms.append(self.patient.date_of_birth.strftime("%d/%m/%Y"))
        terms = " ".join([term for term in terms if term])
        return urllib.parse.quote(terms, safe='')

    def uri(self):
        uri = "{host}/api/organisations/{organisation_id}/patients?q={search_term}".format(
            host=settings.EMIS_API_HOST,
            organisation_id=self.emis_api_config.emis_organisation_id,
            search_term=self.search_term())
        return uri


class GetMedicalRecord(EmisAPIServiceBase):
    def __init__(self, patient_number: str):
        super().__init__()
        self.patient_number = patient_number

    def uri(self) -> str:
        uri = "{host}/api/organisations/{organisation_id}/patients/{patient_number}/medical_record".format(
            host=settings.EMIS_API_HOST,
            organisation_id=self.emis_api_config.emis_organisation_id,
            patient_number=self.patient_number)
        return uri
