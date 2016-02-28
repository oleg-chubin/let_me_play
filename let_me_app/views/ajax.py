'''
Created on Feb 28, 2016

@author: oleg
'''
from django.views.generic.edit import UpdateView
from let_me_app import forms, models
from django.core.urlresolvers import reverse


class RateUserView(UpdateView):
    template_name = "helpers/rate_popup.html"
    form_class = forms.RateForm
    def get_success_url(self):
        return reverse(
            'let_me_help:rate-user', kwargs={'user_id': self.kwargs['user_id']})

    def get_object(self):
        obj, _ = models.CoolnessRate.objects.get_or_create(
            topic_id=self.kwargs['user_id'], rater=self.request.user
        )
        return obj
