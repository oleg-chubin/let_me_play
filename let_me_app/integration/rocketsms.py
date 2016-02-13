'''
Created on Feb 13, 2016

@author: oleg
'''
import requests


class RocketLauncher:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def send_sms(self, phone_number, message_text):
        url = ''.join([self.host.rstrip('/'), '/simple/send'])
        params = {
            'username': self.username,
            'password': self.password,
            'phone': phone_number,
            'text': message_text
        }
        response = requests.post(url, params=params)
        return response.status_code == 200
