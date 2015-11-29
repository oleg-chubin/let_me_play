from django.shortcuts import redirect

from social.pipeline.partial import partial

# Monkey patching - an occasionally necessary evil.
from social import utils
from social.exceptions import InvalidEmail, AuthException

from django.core import signing
from django.core.signing import BadSignature
from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if not email and details.get('username'):
            return
        if email:
            details['email'] = email
        else:
            return redirect('require_email')


def user_password(strategy, user, is_new=False, *args, **kwargs):
    backend = kwargs['backend']
    if backend.name != 'email':
        return

    password = strategy.request_data()['password']
    if is_new:
        user.set_password(password)
        user.save()
    elif not user.check_password(password):
        raise PermissionDenied


def get_user_by_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and details.get('email'):
        user = get_user_model().objects.get(email=details.get('email'))
        return {'is_new': True, 'user': user}
