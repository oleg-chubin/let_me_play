'''
Created on Jul 12, 2015

@author: oleg
'''
import autocomplete_light
from django.utils.translation import ugettext_lazy as _
from let_me_auth.models import User
from let_me_app.models import Equipment, StaffProfile


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['email', '^first_name', '^last_name']
    attrs = {'placeholder': _("Please type to find users")}


class StaffProfileAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['user__email', '^user__first_name', '^user__last_name']
    attrs = {'placeholder': _("Please type to find users")}


class EquipmentAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': _("Please type to find equipment")}

autocomplete_light.register(User, UserAutocomplete)
autocomplete_light.register(Equipment, EquipmentAutocomplete)
autocomplete_light.register(StaffProfile, StaffProfileAutocomplete)

