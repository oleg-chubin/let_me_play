'''
Created on Jul 4, 2015

@author: oleg
'''
from django import template

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)
