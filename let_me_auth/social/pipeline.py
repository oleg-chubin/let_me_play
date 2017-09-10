from django.shortcuts import redirect

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from social.pipeline.partial import partial
from django.db.models import Q
from django.http import HttpResponse
import random
from urllib.parse import urlencode

from logging import getLogger
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

logger = getLogger(__name__)


def send_validation_code(code):
    logger.warn("validation code %s", code)


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


@partial
def got_phone_number(backend, request, strategy, **kwargs):
    if backend.name != 'sms':
        return
    sms_code = strategy.request_data().get('sms_code')
    if sms_code is None:
        code = ''.join(
            random.sample('123456789', settings.VALIDATION_CODE_LENGTH))
        strategy.session_set('validation_code', code)
        send_validation_code(code)
    else:
        correct_sms_code = strategy.session_get('validation_code')
        if correct_sms_code == sms_code:
            try:
                user = get_user_model().objects.get(cell_phone=kwargs['uid'])
            except ObjectDoesNotExist:
                user = get_user_model().objects.create_user(
                    cell_phone=kwargs['uid'])
                created = True
            else:
                created = False
            return {'is_new': created, 'user': user}
    next = strategy.request_data().get('next')
    url = reverse('validate-sms-form')
    if next:
        url = "?".join([url, urlencode({'next': next})])
    return  redirect(url)


def associate_by_unique_fields(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address or cell_phone.
    """
    if user:
        return None

    for unique_field in ['cell_phone', 'email']:
        val = details.get(unique_field)
        if val:
            user = backend.strategy.storage.user.get_user(**{unique_field: val})
    if user:
        return {'user': user, 'is_new': False}
    return None


@partial
def create_name(backend, request, strategy, **kwargs):
    first_name = strategy.request_data().get('user_first_name')
    last_name = strategy.request_data().get('user_last_name')

    if 'user' in kwargs:
        user = get_user_model().objects.get(cell_phone=kwargs['username'])
        first_name = first_name or user.first_name
        last_name = last_name or user.last_name

    if not (first_name and last_name):
        return HttpResponse(strategy.render_html(
            tpl='registration/account_name.html',
            context={'cell_phone': kwargs['username']}
        ))
    else:
        return {'first_name': first_name, 'last_name': last_name}


def associate_user(backend, uid, user=None, social=None, *args, **kwargs):
    if user:
        if not isinstance(uid, str):
            uid = str(uid)
        social = backend.strategy.storage.user.objects.filter(provider=backend.name)
        social = list(social.filter(Q(uid=uid) | Q(user=user)))
        if not social:
            social = backend.strategy.storage.user(provider=backend.name)
        else:
            for obj in social[1:]:
                obj.delete()
            social = social[0]

        social.uid = uid
        social.user = user
        social.save()
        return {'social': social,
                'user': social.user,
                'new_association': True}


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


def get_user_by_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and details.get('email'):
        user = get_user_model().objects.get(email=details.get('email'))
        return {'is_new': True, 'user': user}


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


def email_creator(strategy, details, user=None, is_new=False, *args, **kwargs):
    backend = kwargs['backend']
    if not details.get('email'):
        if details.get('cell_phone'):
            details['email'] = "{}.{}@{}".format(
                details['cell_phone'], backend.name, ABSENT_MAIL_HOST
            )
        else:
            details['email'] = "{}.{}@{}".format(
                details['username'], backend.name, ABSENT_MAIL_HOST
            )
