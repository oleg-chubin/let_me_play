'''
Created on May 31, 2015

@author: oleg
'''
from let_me_app.models import InternalMessage

def get_my_chats(user):
    if user.is_anonymous():
        return InternalMessage.objects.none()
    return InternalMessage.objects.filter(chatparticipant__user=user).order_by('last_update')
