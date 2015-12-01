from django.utils import translation
from django import http
from django.conf import settings
from django.views.generic.base import TemplateView
from django.contrib.admin.templatetags.admin_list import results
from let_me_play import forms
from django.core.urlresolvers import reverse
from django.utils.translation import (check_for_language,
    get_language_from_request, LANGUAGE_SESSION_KEY)

def set_language(request):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'GET':
        lang_code = request.GET.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            translation.activate(lang_code)
    return response


class SettingsView(TemplateView):
    template_name = 'user/settings.html'

    def get_context_data(self, *args, **kwargs):
        result = super(SettingsView, self).get_context_data(*args, **kwargs)
        initial = {'language': get_language_from_request(self.request)}
        result['language_form'] = forms.LanguageForm(
            prefix='language', initial=initial)
        return result
    
    def post(self, request, *args, **kwargs):
        language_form = forms.LanguageForm(prefix='language', data=request.POST)
        response = http.HttpResponseRedirect(reverse('user_settings'))
        if language_form.is_valid():
            lang_code = language_form.cleaned_data['language']
            if lang_code and check_for_language(lang_code):
                if hasattr(request, 'session'):
                    request.session[LANGUAGE_SESSION_KEY] = lang_code
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code,
                                        max_age=settings.LANGUAGE_COOKIE_AGE,
                                        path=settings.LANGUAGE_COOKIE_PATH,
                                        domain=settings.LANGUAGE_COOKIE_DOMAIN)
        return response
            
        
