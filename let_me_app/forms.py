'''
Created on Jul 4, 2015

@author: oleg
'''
from django import forms
from django.contrib.gis import forms as geo_forms

import autocomplete_light
from leaflet.forms.widgets import LeafletWidget
from floppyforms import widgets as floppyforms_widgets

from let_me_app import models
from let_me_auth import models as auth_models


class BootstrapMultipleChoiceWidget(autocomplete_light.MultipleChoiceWidget):
    def build_attrs(self, name=None):
        attrs = super(BootstrapMultipleChoiceWidget, self).build_attrs(name=name)
        attrs['class'] = attrs['class'] + ' form-control'
        return attrs


class BootstrapChoiceWidget(autocomplete_light.ChoiceWidget):
    def build_attrs(self, name=None):
        attrs = super(BootstrapChoiceWidget, self).build_attrs(name=name)
        attrs['class'] = attrs['class'] + ' form-control'
        return attrs


class BootstrapModelMultipleChoiceField(autocomplete_light.ModelMultipleChoiceField):
    widget=BootstrapMultipleChoiceWidget

class ChatMessageForm(forms.Form):
    message = forms.CharField()


class EventProposalForm(forms.Form):
    users = BootstrapModelMultipleChoiceField('UserAutocomplete')
    comment = forms.CharField(required=False)


class InventoryForm(forms.ModelForm):
    class Meta:
        model = models.Inventory
        fields = ['equipment', 'amount']
        widgets = {
            'equipment': BootstrapChoiceWidget('EquipmentAutocomplete'),
            'amount': floppyforms_widgets.NumberInput(),
        }


class GroupAdminForm(forms.Form):
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
    activity_type = forms.ModelMultipleChoiceField(
        models.ActivityType.objects.all(),
        required=False, widget=floppyforms_widgets.SelectMultiple()
    )

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


class EventVisitForm(forms.Form):
    users = BootstrapModelMultipleChoiceField('UserAutocomplete')