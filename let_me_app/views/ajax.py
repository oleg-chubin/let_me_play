'''
Created on Feb 28, 2016

@author: oleg
'''
from django.views.generic.edit import UpdateView
from let_me_app import forms, models
from let_me_auth import forms as auth_forms
from let_me_auth import models as auth_models
from django.core.urlresolvers import reverse


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
    model = models.Group

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


