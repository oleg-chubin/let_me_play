'''
Created on Jul 4, 2015

@author: oleg
'''
from django import forms
from django.contrib.gis import forms as geo_forms
from django.utils.translation import ugettext_lazy as _

import autocomplete_light
from leaflet.forms.widgets import LeafletWidget
from floppyforms import widgets as floppyforms_widgets

from let_me_app import models
from django.forms.models import BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME


class BootstrapMultipleChoiceWidget(autocomplete_light.MultipleChoiceWidget):
    def build_attrs(self, name=None):
        attrs = super(BootstrapMultipleChoiceWidget, self).build_attrs(name=name)
        attrs['class'] = attrs['class'] + ' form-control'
        return attrs


class BootstrapChoiceWidget(autocomplete_light.ChoiceWidget):
    def build_attrs(self, *args, **kwargs):
        attrs = super(BootstrapChoiceWidget, self).build_attrs(*args, **kwargs)
        attrs['class'] = attrs['class'] + ' form-control'
        return attrs


class BootstrapModelMultipleChoiceField(autocomplete_light.ModelMultipleChoiceField):
    widget=BootstrapMultipleChoiceWidget


class TrashCheckboxInput(floppyforms_widgets.CheckboxInput):
    template_name = 'floppyforms/trash_checkbox.html'


class AddonCheckbox(floppyforms_widgets.CheckboxInput):
    template_name = 'floppyforms/addon_checkbox.html'


class ReadonlySelect(floppyforms_widgets.Select):
    template_name = 'floppyforms/readonly.html'


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
        fields = ('name', 'description', 'geo_point', 'geo_line', 'address')
        widgets = {'geo_point': LeafletWidget(), 'geo_line': LeafletWidget()}


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields = ('name', 'description', 'geo_point', 'geo_line', 'address')
        widgets = {
            'geo_point': LeafletWidget(),
            'description': floppyforms_widgets.Textarea(),
            'name': floppyforms_widgets.TextInput(),
            'address': floppyforms_widgets.Textarea(),
            'geo_line': LeafletWidget()
        }


class CourtForm(forms.ModelForm):
    class Meta:
        model = models.Court
        exclude = ('site', 'admin_group')
        widgets = {
            'description': floppyforms_widgets.Textarea(),
            'activity_type': floppyforms_widgets.Select(),
        }


class CourtSearchForm(forms.Form):
    geo_point = geo_forms.PointField(
        required=False, widget=floppyforms_widgets.HiddenInput())
    radius = forms.IntegerField(
        label=_("radius"), required=False, widget=floppyforms_widgets.NumberInput())
    activity_type = forms.ModelMultipleChoiceField(
        models.ActivityType.objects.all(), label=_("activity type"),
        required=False, widget=floppyforms_widgets.SelectMultiple()
    )


class EventSearchForm(forms.Form):
    start_date = forms.DateTimeField(
        label=_("start date"), required=False,
        widget=floppyforms_widgets.DateTimeInput())
    end_date = forms.DateTimeField(
        label=_("end date"), required=False, widget=floppyforms_widgets.DateTimeInput())
    geo_point = geo_forms.PointField(
        required=False, widget=floppyforms_widgets.HiddenInput())
    radius = forms.IntegerField(
        label=_("radius"), required=False, widget=floppyforms_widgets.NumberInput())
    activity_type = forms.ModelMultipleChoiceField(
        models.ActivityType.objects.all(), label=_("activity type"),
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
            'preliminary_price': floppyforms_widgets.NumberInput()
        }

    class Media:
        css = {
            'all': ('css/bootstrap-datetimepicker.css',)
        }
        js = ('js/moment.js', 'js/bootstrap-datetimepicker.js', 'js/forms.js')


class EventVisitForm(forms.Form):
    users = BootstrapModelMultipleChoiceField('UserAutocomplete')


class EventStaffForm(forms.ModelForm):
    class Meta:
        model = models.EventStaff
        fields = ('staff', 'event', 'invoice', 'role')
        widgets = {
            'staff': BootstrapChoiceWidget('StaffProfileAutocomplete'),
            'event': floppyforms_widgets.HiddenInput(),
            'invoice': floppyforms_widgets.HiddenInput(),
            'role': floppyforms_widgets.Select()
        }

    def __init__(self, *args, **kwargs):
        super(EventStaffForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget.is_required = False


class CustomInlineFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(CustomInlineFormset, self).add_fields(form, index)
        if self.can_delete:
            form.fields[DELETION_FIELD_NAME] = forms.BooleanField(
                label=_('Delete'), required=False, widget=TrashCheckboxInput)


EventStaffFormSet = forms.inlineformset_factory(
    models.Event, models.EventStaff, formset=CustomInlineFormset,
    form=EventStaffForm, extra=2
)


class CompleteEventVisitForm(forms.ModelForm):
    income = forms.IntegerField(
        label=_("Income"), required=False, widget=floppyforms_widgets.NumberInput)
    status = forms.BooleanField(
        label=_("Visit was payed"), required=False,
        widget=AddonCheckbox)

    class Meta:
        model = models.Visit
        fields = ('status', 'receipt', 'income', 'user')
        widgets = {
            'receipt': floppyforms_widgets.HiddenInput(),
            'user': ReadonlySelect(),
        }

    class Media:
        js = ('js/complete_event_form.js', )

    def clean_status(self):
        if self.cleaned_data['status']:
            return models.VisitStatuses.COMPLETED
        else:
            return models.VisitStatuses.MISSED


CompleteEventVisitFormSet = forms.inlineformset_factory(
    models.Event, models.Visit, formset=CustomInlineFormset,
    form=CompleteEventVisitForm, extra=0, can_delete=False
)


class VisitIndexForm(forms.ModelForm):
    value = forms.FloatField(
        label=_("Value"), required=False, widget=floppyforms_widgets.TextInput)
    parametr = forms.ModelChoiceField(
        models.IndexParametr.objects.all(), label=_("Parametr"),
        required=False, widget=floppyforms_widgets.Select)

    class Meta:
        fields = ('value', 'parametr')
        model = models.VisitIndex


VisitIndexFormSet = forms.inlineformset_factory(
    models.Visit, models.VisitIndex, formset=CustomInlineFormset,
    form=VisitIndexForm, extra=1
)


class CoachRecommendationForm(forms.ModelForm):
    recommendation = forms.CharField(
        label=_("Value"), required=False,
        widget=floppyforms_widgets.Textarea(attrs={"data-provide": "markdown"})
    )

    class Meta:
        model = models.CoachRecommendation
        fields = ('recommendation',)

    class Media:
        js = (
            'js/bootstrap-markdown.js',
            'js/markdown.js',
            'js/to-markdown.js',
            'js/bootstrap-markdown.ru.js',
        )
        css = {
            'all': (
                'css/bootstrap-markdown.min.css',
            )
        }



CoachRecommendationFormSet = forms.inlineformset_factory(
    models.Visit, models.CoachRecommendation, formset=CustomInlineFormset,
    form=CoachRecommendationForm, extra=1, max_num=1, can_delete=False
)




