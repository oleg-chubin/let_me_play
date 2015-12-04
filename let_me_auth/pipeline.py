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


ABSENT_MAIL_HOST = "no.mail.for.me"


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


def email_creator(strategy, details, user=None, is_new=False, *args, **kwargs):
    backend = kwargs['backend']
    request = kwargs['request']
    if not details.get('email'):
        details['email'] = "{}.{}@{}".format(
            details['username'], backend.name, ABSENT_MAIL_HOST
        )

def get_user_from_verification_code(backend, details, is_new=False, user=None, *args, **kwargs):
    if backend.name != 'email':
        return

    data = backend.strategy.request_data()
    if 'verification_code' in data:
        users = get_user_model().objects.filter(newcomer__code=data['verification_code'])[:1]
        if users:
            user = users[0]
            if not user.is_active:
                user.is_active = True
                user.save()

    if user:
        return {'is_new': False, 'user': user}


def mail_validation(backend, details, is_new=False, user=None, *args, **kwargs):
    if backend.name == 'email':
        if user.is_active:
            if is_new:
                user.is_active = False
                user.save()
            else:
                return backend.strategy.redirect('login')
    else:
        if not user.is_active:
            user.is_active = True
            user.save()
        return

    info, _ = user.newcomer_set.get_or_create()
    code = backend.strategy.send_email_validation(backend, details['email'])
    info.code = code.code
    info.save()
    return backend.strategy.redirect(
        backend.strategy.setting('EMAIL_VALIDATION_URL')
    )


def user_password(strategy, user, is_new=False, *args, **kwargs):
    backend = kwargs['backend']

    if backend.name != 'email' or (is_new or backend.setting('PASSWORDLESS', False)):
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
