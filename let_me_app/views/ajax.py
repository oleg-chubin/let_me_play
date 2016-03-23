'''
Created on Feb 28, 2016

@author: oleg
'''
from django.views.generic.edit import UpdateView
from let_me_app import forms, models
from let_me_auth import forms as auth_forms
from let_me_auth import models as auth_models
from django.core.urlresolvers import reverse
from let_me_auth.models import FollowerGroup


class RateUserView(UpdateView):
    template_name = "helpers/rate_popup.html"
    form_class = forms.RateForm
    def get_success_url(self):
        return reverse(
            'let_me_help:rate-user', kwargs={'user_id': self.kwargs['user_id']})

    def get_object(self):
        rates = models.CoolnessRate.objects.filter(
            topic_id=self.kwargs['user_id'], rater=self.request.user
        )

        if rates:
            return rates[0]

        return models.CoolnessRate(
            topic_id=self.kwargs['user_id'], rater=self.request.user
        )


class ManageGroup(UpdateView):
    template_name = "helpers/manage_group.html"
    form_class = forms.GroupForm
    model = auth_models.FollowerGroup

    def get_success_url(self):
        return reverse(
            'let_me_help:update-group', kwargs={'pk': self.object.id})

    def check_permission(self, group_object):
        follower_group = auth_models.FollowerGroup.objects.filter(
            group_ptr_id=group_object.id)
        if not follower_group:
            return True
        follower_group = follower_group[0]
        if self.request.user.id == follower_group.followable_id:
            return True
        user = auth_models.User.objects.filter(
            groups__court__followable_ptr_id=follower_group.followable_id,
            id=self.request.user.id)
        if user.exists():
            return True
        return False

    def get_object(self):
        obj = super(ManageGroup, self).get_object()
        self.check_permission(obj)
        return obj


class PublishEventView(UpdateView):
    template_name = "helpers/publish_event.html"
    form_class = forms.PublishEventForm
    model = models.Event

    def get_success_url(self):
        return reverse(
            'let_me_help:publish-event', kwargs={'pk': self.object.id})

    def check_permission(self, event):
        return event.court.admin_group.user_set.filter(
            id=self.request.user.id).exists()

    def get_form(self, form_class=None):
        form = super(PublishEventView, self).get_form(form_class=form_class)
        event = models.Event.objects.get(id=self.kwargs['pk'])
        form.fields['target_groups'].queryset = FollowerGroup.objects.filter(
            followable=event.court_id) |  FollowerGroup.objects.filter(name="anyone")
        return form

    def get_object(self):
        obj = super(PublishEventView, self).get_object()
        self.check_permission(obj)
        return obj


