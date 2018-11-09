import json
import requests
from django.conf import settings

class AuthMobile:
    def __init__(self, **kwargs):
        self.url = "https://api.checkmobi.com/v1/validation/"
        self.header = {
            "Authorization": settings.CHECKMOBI_SECRET_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.number = kwargs.get('number')
        self.mobi_id = kwargs.get('mobi_id')
        self.pin = kwargs.get('pin')

    def request(self):
        data=json.dumps({"number": self.number, "type": "sms", "platform": "web"})
        response = requests.post(self.url + "request", data, headers=self.header)
        return response

    def verify(self):
        data=json.dumps({"id": self.mobi_id, "pin": self.pin})
        response = requests.post(self.url + "verify", data, headers=self.header)
        return response
