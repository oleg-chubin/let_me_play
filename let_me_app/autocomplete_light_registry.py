'''
Created on Jul 12, 2015

@author: oleg
'''
import autocomplete_light
from let_me_auth.models import User
from let_me_app.models import Equipment


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['email', '^first_name', 'last_name']
    attrs = {'placeholder': "Please type to find users"}


class EquipmentAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': "Please type to find equipment"}

autocomplete_light.register(User, UserAutocomplete)
autocomplete_light.register(Equipment, EquipmentAutocomplete)

