from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# from django.template.context import RequestContext
from annoying.decorators import render_to
from django.template.context import RequestContext
from django.utils.translation import gettext as _
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from let_me_auth.models import User
from django.views.generic.edit import UpdateView, BaseUpdateView, BaseCreateView
from let_me_auth.forms import UserDetailsForm
from let_me_auth import models
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse, HttpResponseRedirect
from let_me_app.integration.rocketsms import RocketLauncher
import random


def context(**extra):
    return dict(**extra)


@login_required()
def home(request):
    return redirect(reverse(settings.DEFAULT_VIEW_NAME))


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
@render_to('home.html')
def done(request):
    """Login complete view, displays user data"""
    return context()


@render_to('registration/login.html')
def validation_sent(request):
    return context(
        validation_sent=True,
        email=request.session.get('email_validation_address')
    )


class CustomSetPasswordForm(SetPasswordForm):
    verification_code = forms.CharField(widget=forms.HiddenInput)

    def save(self, commit=True):
        self.user.is_active = True
        return super(CustomSetPasswordForm, self).save(commit=commit)


@render_to('registration/login.html')
def set_password(request):
    post_reset_redirect = "/"
    code = request.REQUEST.get('verification_code')
    user = User.objects.filter(newcomer__code=code)[:1]
    if not user or user[0].is_active:
        return redirect('login')
    else:
        user = user[0]

    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(post_reset_redirect)
    else:
        form = CustomSetPasswordForm(user, initial={'verification_code': code})
    return {'form': form, 'initial_password': True}


@render_to('registration/login.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)


@render_to('registration/login.html')
def signup(request):
    return context(signup=True)


class ProfileDetailsView(DetailView):
    template_name = 'user/profile_details.html'
    model = models.User

    def get_object(self, **kwargs):
        return self.request.user


class EditUserView(UpdateView):
    form_class = UserDetailsForm
    template_name = 'user/details_form.html'

    def get_success_url(self):
        return reverse('let_me_auth:profile_details')

    def get_object(self):
        return self.request.user.user


class CreateConfirmationCodeView(TemplateView):
    def post(self, request, *args, **kwargs):
        confirmation, created = models.ConfirmationCodes.objects.get_or_create(
            user=request.user)
        confirmation.code = ''.join(
            [str(i) for i in random.sample(range(1, 10), 5)])
        confirmation.save()
        sms_sender = RocketLauncher(**settings.ROCKET_SMS_CONFIG)
        import ipdb; ipdb.set_trace()
        sms_text = _(
            "Confirmation code is %(phone)s.") % {'phone': confirmation.code}
        sms_sender.send_sms(request.user.cell_phone, sms_text)
        return HttpResponse()


class CheckConfirmationCodeView(BaseUpdateView):
    def post(self, request, *args, **kwargs):
        confirmation = models.ConfirmationCodes.objects.filter(
            user=request.user)
        if confirmation and confirmation[0].code == request.POST.get('code'):
            self.request.user.cell_phone_is_valid = True
            self.request.user.save()
        return HttpResponseRedirect(reverse('let_me_auth:profile_details'))

