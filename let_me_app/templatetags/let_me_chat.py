'''
Created on Jul 4, 2015

@author: oleg
'''
from datetime import datetime
from django.utils import timezone
from xml.dom import minidom
from django import template

register = template.Library()


@register.filter(name='recent_chat_message')
def recent_chat_message(chat_thread):
    participants = chat_thread.chatparticipant_set.all()
    participants = {i.id: i.user for i in participants}
    parsed = minidom.parseString("<body>{}</body>".format(chat_thread.text))
    message_node = parsed.firstChild.getElementsByTagName('message')[0]
    text = message_node.getElementsByTagName('text')
    text = text and text[0].firstChild.nodeValue

    author = message_node.getElementsByTagName('author')
    author = author and int(author[0].firstChild.nodeValue.strip())

    date = message_node.getElementsByTagName('date')
    if date:
        date = date[0].firstChild.nodeValue.strip()
        date = datetime.strptime(
            ''.join(date.rsplit(':', 1)), '%Y-%m-%d %H:%M:%S.%f%z')
    return {'text': text, 'author': participants[author], 'date': date}