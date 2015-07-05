'''
Created on Jul 4, 2015

@author: oleg
'''
from django.forms import Form, CharField


class ChatMessageForm(Form):
    message = CharField()