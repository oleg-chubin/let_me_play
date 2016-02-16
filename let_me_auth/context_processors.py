'''
Created on Jul 3, 2015

@author: oleg
'''
from let_me_auth import models


def user_sex(request):
    return {
        'USER_SEX': models.Sex,
    }
