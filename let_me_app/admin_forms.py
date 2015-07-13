'''
Created on Jul 4, 2015

@author: oleg
'''
from django import forms
from leaflet.forms.widgets import LeafletWidget

from let_me_app import models


class SiteAdminForm(forms.ModelForm):

    class Meta:
        model = models.Site
        widgets = {'geo_point': LeafletWidget()}
