from django.utils import translation
from django import http
from django.conf import settings
from django.views.generic.base import TemplateView
from django.contrib.admin.templatetags.admin_list import results
from let_me_play import forms
from django.core.urlresolvers import reverse
from django.utils.translation import (check_for_language,
    get_language_from_request, LANGUAGE_SESSION_KEY)

# def set_language(request):
#     next = request.REQUEST.get('next', None)
#     if not next:
#         next = request.META.get('HTTP_REFERER', None)
#     if not next:
#         next = '/'
#     response = http.HttpResponseRedirect(next)
#     if request.method == 'GET':
#         lang_code = request.GET.get('language', None)
#         if lang_code and check_for_language(lang_code):
#             if hasattr(request, 'session'):
#                 request.session['django_language'] = lang_code
#             else:
#                 response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
#             translation.activate(lang_code)
#     return response


