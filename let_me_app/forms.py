'''
Created on Jul 4, 2015

@author: oleg
'''
from django.forms import Form, CharField
from django import forms
from django.contrib.gis import forms as geo_forms

import autocomplete_light
from leaflet.forms.widgets import LeafletWidget
from floppyforms import widgets as floppyforms_widgets

from let_me_app import models


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


class SiteAdminForm(forms.ModelForm):
    class Meta:
        model = models.Site
        widgets = {'geo_point': LeafletWidget()}


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        widgets = {
            'geo_point': LeafletWidget(),
            'description': floppyforms_widgets.Textarea(),
            'name': floppyforms_widgets.TextInput(),
            'address': floppyforms_widgets.Textarea()
        }


class CourtForm(forms.ModelForm):
    class Meta:
        model = models.Court
        exclude = ('site', 'admin_group')
        widgets = {
            'description': floppyforms_widgets.Textarea(),
            'activity_type': floppyforms_widgets.Select(),
        }


class EventSearchForm(forms.Form):
    start_date = forms.DateTimeField(
        required=False, widget=floppyforms_widgets.DateTimeInput())
    end_date = forms.DateTimeField(
        required=False, widget=floppyforms_widgets.DateTimeInput())
    geo_point = geo_forms.PointField(
        required=False, widget=floppyforms_widgets.HiddenInput())
    radius = forms.IntegerField(
        required=False, widget=floppyforms_widgets.NumberInput())
    class Media:
        css = {
            'all': ('css/bootstrap-datetimepicker.css',)
        }
        js = ('js/moment.js', 'js/bootstrap-datetimepicker.js', 'js/forms.js')


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ('court', 'invoice', 'inventory_list', 'staff', 'status')
        widgets = {
            'start_at': floppyforms_widgets.DateTimeInput(),
            'description': floppyforms_widgets.Textarea(),
            'name': floppyforms_widgets.TextInput(),
        }

    class Media:
        css = {
            'all': ('css/bootstrap-datetimepicker.css',)
        }
        js = ('js/moment.js', 'js/bootstrap-datetimepicker.js', 'js/forms.js')
