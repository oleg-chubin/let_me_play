'''
Created on Jul 4, 2015

@author: oleg
'''
from django.forms import Form, CharField
import autocomplete_light


class BootstrapMultipleChoiceWidget(autocomplete_light.MultipleChoiceWidget):
    def build_attrs(self, name=None):
        attrs = super(BootstrapMultipleChoiceWidget, self).build_attrs(name=name)
        attrs['class'] = attrs['class'] + ' form-control'
        return attrs


class BootstrapModelMultipleChoiceField(autocomplete_light.ModelMultipleChoiceField):
    widget=BootstrapMultipleChoiceWidget

class ChatMessageForm(Form):
    message = CharField()


class EventProposalForm(Form):
    users = BootstrapModelMultipleChoiceField('UserAutocomplete')
    comment = CharField()


class GroupAdminForm(Form):
    users = BootstrapModelMultipleChoiceField('UserAutocomplete')
