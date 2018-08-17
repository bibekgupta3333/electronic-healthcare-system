class DummyPatient(object):
    def __init__(self, first_name, last_name, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = date_of_birth


class DummyPractice(object):
    def __init__(self, emis_username, emis_password, external_organisation_id):
        self.emis_username = emis_username
        self.emis_password = emis_password
        self.external_organisation_id = external_organisation_id
