'''
Created on Jul 4, 2015

@author: oleg
'''
from django import forms
from django.contrib.gis import forms as geo_forms
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from leaflet.forms.widgets import LeafletWidget
from floppyforms import widgets as floppyforms_widgets

from let_me_app import models
from let_me_auth import models as auth_models
from django.forms.models import BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
import slugify
from let_me_auth.models import User, FollowerGroup
from let_me_auth.social.pipeline import ABSENT_MAIL_HOST
from embed_video.fields import EmbedVideoFormField


class BootstrapMultipleChoiceWidget(autocomplete.ModelSelect2Multiple):
    def build_attrs(self, *args, **kwargs):
        attrs = super(BootstrapMultipleChoiceWidget, self).build_attrs(*args, **kwargs)
        attrs['class'] = attrs.get('class', '') + ' form-control'
        return attrs


class BootstrapChoiceWidget(autocomplete.ModelSelect2):
    def build_attrs(self, *args, **kwargs):
        attrs = super(BootstrapChoiceWidget, self).build_attrs(*args, **kwargs)
        attrs['class'] = attrs.get('class', '') + ' form-control'
        return attrs


class TrashCheckboxInput(floppyforms_widgets.CheckboxInput):
    template_name = 'floppyforms/trash_checkbox.html'


class AddonCheckbox(floppyforms_widgets.CheckboxInput):
    template_name = 'floppyforms/addon_checkbox.html'


class ReadonlySelect(floppyforms_widgets.Select):
    template_name = 'floppyforms/readonly.html'


class ImageRadioSelect(floppyforms_widgets.RadioSelect):
    template_name = "floppyforms/image_radio_select.html"

    def get_context_data(self):
        return {'COOLNESS_IMAGES': models.Coolness.IMAGES}

    class Media:
        css = {
            'all': ('css/imaged_checkboxes.css',)
        }
        js = ('js/imaged_radiobuttons.js',)


class CheckboxUserSelectMultiple(floppyforms_widgets.CheckboxSelectMultiple):
    template_name = "floppyforms/checkbox_user_select.html"

    class Media:
        css = {
            'all': ('css/imaged_checkboxes.css',)
        }
        js = ('js/imaged_checkboxes.js',)


class CustomImageInput(floppyforms_widgets.ClearableFileInput):
    template_name = "floppyforms/image_input.html"
    class Media:
        css = {
            'all': ('css/image_input.css',)
        }
        js = ('js/image_input.js',)


class ChatMessageForm(forms.Form):
    message = forms.CharField()


class RateForm(forms.ModelForm):
    class Meta:
        fields = ['value']
        widgets = {
            'value': ImageRadioSelect,
        }
        model = models.CoolnessRate


class EventProposalForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=auth_models.User.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete'))
    comment = forms.CharField(
        required=False, widget=floppyforms_widgets.Textarea)
    known_users = forms.ModelMultipleChoiceField(
        queryset=auth_models.User.objects.all(),
        required=False,
        widget=CheckboxUserSelectMultiple)


class InventoryForm(forms.ModelForm):
    class Meta:
        model = models.Inventory
        fields = ['equipment', 'amount']
        widgets = {
            'equipment': BootstrapChoiceWidget(url='equipment-autocomplete'),
            'amount': floppyforms_widgets.NumberInput(),
        }


class GroupAdminForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=auth_models.User.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete'))


class PublishEventForm(forms.ModelForm):
    target_groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=auth_models.FollowerGroup.objects.filter(name="anyone"),
        widget=floppyforms_widgets.CheckboxSelectMultiple)

    class Meta:
        model = models.Event
        fields = ('target_groups', )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['target_groups'] = instance.target_groups.all()
            kwargs['initial'] = initial
        super(PublishEventForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        event = super(PublishEventForm, self).save(commit=commit)

        if commit:
            event.target_groups = self.cleaned_data['target_groups']
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                event.target_groups = self.cleaned_data['target_groups']
            self.save_m2m = new_save_m2m
        return event


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


class GroupForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=auth_models.User.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete'))

    class Meta:
        model = FollowerGroup
        fields = ('users', 'verbose_name')
        widgets = {
            'verbose_name': floppyforms_widgets.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['users'] = instance.user_set.all()
            kwargs['initial'] = initial
        super(GroupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        group = super(GroupForm, self).save(commit=commit)

        if commit:
            group.user_set = self.cleaned_data['users']
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                group.user_set = self.cleaned_data['users']
            self.save_m2m = new_save_m2m
        return group


class CourtForm(forms.ModelForm):
    class Meta:
        model = models.Court
        exclude = ('site', 'admin_group')
        widgets = {
            'name': floppyforms_widgets.TextInput(),
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


class EventForm(PublishEventForm):
    class Meta:
        model = models.Event
        exclude = ('court', 'invoice', 'inventory_list', 'staff', 'status')
        widgets = {
            'start_at': floppyforms_widgets.DateTimeInput(),
            'description': floppyforms_widgets.Textarea(),
            'name': floppyforms_widgets.TextInput(),
            'preliminary_price': floppyforms_widgets.TextInput()
        }

    class Media:
        css = {
            'all': ('css/bootstrap-datetimepicker.css',)
        }
        js = ('js/moment.js', 'js/bootstrap-datetimepicker.js', 'js/forms.js')


class UserCreateMultipleField(autocomplete.QuerySetSequenceModelMultipleField):
    def create_value(self, value):
        parts = value.split(' ', 1)
        first_name = parts[0].strip()
        email_parts = [slugify.slugify(first_name)]
        defaults = {'first_name': first_name}
        if len(parts) > 1:
            last_name = parts[1].strip()
            defaults['last_name'] = last_name
            email_parts.append(slugify.slugify(last_name))
        email = '@'.join(['.'.join(email_parts), ABSENT_MAIL_HOST])
        user, _ = User.objects.get_or_create(email=email, defaults=defaults)
        return user.id


class EventVisitForm(forms.Form):
    users = UserCreateMultipleField(
        queryset=auth_models.User.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete'))


class ExtendedEventVisitForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=auth_models.User.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete'))
    known_users = forms.ModelMultipleChoiceField(
        queryset=auth_models.User.objects.all(),
        required=False,
        widget=CheckboxUserSelectMultiple)


class EventVisitRoleForm(forms.Form):
    roles = forms.ModelMultipleChoiceField(
        queryset=models.StaffRole.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='staffrole-autocomplete'))


class GalleryImagesForm(forms.ModelForm):
    class Meta:
        model = models.GalleryImage
        fields = ('image', 'note')
        widgets = {
            'note': floppyforms_widgets.Textarea(attrs={'rows': 2}),
            'image': CustomImageInput(),
        }


class GalleryVideoForm(forms.ModelForm):
    video = EmbedVideoFormField(
        required=False, widget=floppyforms_widgets.URLInput())

    class Meta:
        model = models.GalleryVideo
        fields = ('video', 'note')
        widgets = {
            'note': floppyforms_widgets.Textarea(attrs={'rows': 2}),
        }


class CustomInlineFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(CustomInlineFormset, self).add_fields(form, index)
        if self.can_delete:
            form.fields[DELETION_FIELD_NAME] = forms.BooleanField(
                label=_('Delete'), required=False, widget=TrashCheckboxInput)


GalleryImagesFormset = forms.inlineformset_factory(
    models.Event, models.GalleryImage, formset=CustomInlineFormset,
    form=GalleryImagesForm, extra=2
)

GalleryVideoFormset = forms.inlineformset_factory(
    models.Event, models.GalleryVideo, formset=CustomInlineFormset,
    form=GalleryVideoForm, extra=2
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
