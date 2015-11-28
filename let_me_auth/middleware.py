'''
Created on Jul 22, 2015

@author: oleg
'''
from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile
from urllib.parse import urlencode


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

if hasattr(settings, 'LOGIN_EXEMPT_NAMESPACES'):
    LOGIN_EXEMPT_NAMESPACES = settings.LOGIN_EXEMPT_NAMESPACES


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."
        if not request.user.is_authenticated():
            path = request.path_info.lstrip('/')
            if not (any(m.match(path) for m in EXEMPT_URLS) or
                    request.resolver_match.namespace in LOGIN_EXEMPT_NAMESPACES):
                login_path = settings.LOGIN_URL
                if path and path != login_path:
                    login_path = "%s?%s" % (login_path, urlencode({'next': path}))
                return HttpResponseRedirect(login_path)
