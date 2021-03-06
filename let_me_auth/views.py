from django.shortcuts import redirect, render
from django.conf import settings
from django import http
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# from django.template.context import RequestContext
from annoying.decorators import render_to
from django.utils.translation import gettext as _
from let_me_auth.models import User
from django.views.generic.edit import UpdateView, BaseUpdateView
from django.utils.translation import (check_for_language,
    get_language_from_request, LANGUAGE_SESSION_KEY)
from let_me_auth.forms import UserDetailsForm
from let_me_auth import models, forms
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.http.response import HttpResponse, HttpResponseRedirect
from let_me_app.integration.rocketsms import RocketLauncher
import random
from datetime import datetime
from django.utils import timezone


def context(**extra):
    return dict(**extra)


@login_required()
def home(request):
    return redirect(reverse(settings.DEFAULT_VIEW_NAME))


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@render_to('registration/login.html')
def login_user(request):
    logout(request)
    return context(
        signup=True, facebook_app_id=settings.SOCIAL_AUTH_ACCOUNT_KIT_KEY
    )


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
        form = forms.CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(post_reset_redirect)
    else:
        form = forms.CustomSetPasswordForm(
            user, initial={'verification_code': code})
    return {'form': form, 'initial_password': True}


@render_to('registration/login.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)


@render_to('registration/login.html')
def signup(request):
    return context(
        signup=True, facebook_app_id=settings.SOCIAL_AUTH_ACCOUNT_KIT_KEY
    )


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
        if not created and confirmation.created_at > timezone.now()-settings.SMS_CONFIRMATION_COOLDOWN:
            return HttpResponse()

        if not created:
            confirmation.delete()
            confirmation = models.ConfirmationCodes(user=request.user)
        confirmation.code=''.join(
            [str(i) for i in random.sample(range(1, 10), 5)])
        confirmation.save()
        sms_sender = RocketLauncher(**settings.ROCKET_SMS_CONFIG)
        sms_text = _(
            "Confirmation code %(phone)s. Is valid for %(x)s minutes") % {
                'phone': confirmation.code,
                'x': settings.SMS_CONFIRMATION_COOLDOWN.seconds/60
            }
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


class SettingsView(TemplateView):
    template_name = 'user/settings.html'

    def get_context_data(self, *args, **kwargs):
        result = super(SettingsView, self).get_context_data(*args, **kwargs)
        instance, _ = models.NotificationSettings.objects.get_or_create(
            user_id=self.request.user.id,
            defaults={
                'sms_notifications': False,
                'email_notifications': False,
                'lang': get_language_from_request(self.request)})
        result['language_form'] = forms.NotificationSettingsForm(
            prefix='notifications', instance=instance, data=kwargs.get('data'))
        return result

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(data=request.POST)
        language_form = context['language_form']
        response = http.HttpResponseRedirect(
            reverse('let_me_auth:user_settings'))
        if language_form.is_valid():
            lang_code = language_form.cleaned_data['lang']
            if lang_code and check_for_language(lang_code):
                if hasattr(request, 'session'):
                    request.session[LANGUAGE_SESSION_KEY] = lang_code
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code,
                                        max_age=settings.LANGUAGE_COOKIE_AGE,
                                        path=settings.LANGUAGE_COOKIE_PATH,
                                        domain=settings.LANGUAGE_COOKIE_DOMAIN)
            language_form.save()
        return response

