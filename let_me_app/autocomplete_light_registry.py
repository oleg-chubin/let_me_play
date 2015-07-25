'''
Created on Jul 12, 2015

@author: oleg
'''
import autocomplete_light
from let_me_auth.models import User


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['email', '^first_name', 'last_name']
    attrs = {'placeholder': "Please type to find users"}

autocomplete_light.register(User, UserAutocomplete)

