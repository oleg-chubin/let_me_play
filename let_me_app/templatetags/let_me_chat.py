'''
Created on Jul 4, 2015

@author: oleg
'''
from datetime import datetime
from django.utils import timezone
from xml.dom import minidom
from django import template

register = template.Library()


def get_chat_messages(chat_xml, participants):
    parsed = minidom.parseString("<body>{}</body>".format(chat_xml))
    for message_node in parsed.firstChild.getElementsByTagName('message'):
        text = message_node.getElementsByTagName('text')
        text = text and text[0].firstChild.nodeValue

        author = message_node.getElementsByTagName('author')
        author = author and int(author[0].firstChild.nodeValue.strip())

        date = message_node.getElementsByTagName('date')
        if date:
            date = date[0].firstChild.nodeValue.strip()
            date = datetime.strptime(
                ''.join(date.rsplit(':', 1)), '%Y-%m-%d %H:%M:%S.%f%z')
        yield {'text': text, 'author': participants[author], 'date': date}


@register.filter(name='recent_chat_message')
def recent_chat_message(chat_thread):
    participants = chat_thread.chatparticipant_set.all()
    participants = {i.user_id: i.user for i in participants}
    return next(iter(get_chat_messages(chat_thread.text, participants)))


@register.filter(name='chat_messages')
def chat_messages(chat_thread):
    participants = chat_thread.chatparticipant_set.all()
    participants = {i.user_id: i.user for i in participants}
    distinct_messages = list(get_chat_messages(chat_thread.text, participants))
    return reversed(distinct_messages)
