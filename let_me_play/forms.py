'''
Created on Aug 16, 2015

@author: oleg
'''
from django import forms
from django.utils.translation import ugettext as _
from django.conf import settings



class BootstrapChoiceWidget(forms.Select):
    def build_attrs(self, *args, **kwargs):
        attrs = super(BootstrapChoiceWidget, self).build_attrs(*args, **kwargs)
        attrs['class'] = attrs.get('class', '') + ' form-control'
        return attrs


class LanguageForm(forms.Form):
    language = forms.ChoiceField(
        label=_('language'), 
        choices=settings.LANGUAGES, 
        widget=BootstrapChoiceWidget()
    )
