"""
Legacy Email backend, docs at:
    http://psa.matiasaguirre.net/docs/backends/email.html
"""
import hmac
import hashlib
from requests import request, ConnectionError

from social.utils import user_agent
from social.exceptions import AuthFailed
from social.backends.legacy import LegacyAuth


class AccountKitMixin(object):
    def get_access_token(self, key, secret, code):
        app_access_token = '|'.join(['AA', key, secret])
        params = {
          'grant_type': 'authorization_code',
          'code': code,
          'access_token': app_access_token
        }

        res = self.get_json(
            'https://graph.accountkit.com/v1.0/access_token',
            params=params,
            method='GET'
        )

        return  res['access_token']

    def get_account_details(self, secret, access_token):
        appsecret_proof = hmac.new(
            secret.encode('utf-8'), access_token.encode('utf-8'), hashlib.sha256
        )
        res = self.get_json(
            'https://graph.accountkit.com/v1.0/me',
            params={
                'access_token': access_token,
                'appsecret_proof': appsecret_proof.hexdigest()
            },
            method='GET'
        )

        return (res['phone']['number'].strip('+'), res)


class AccountKitAuth(LegacyAuth, AccountKitMixin):
    name = 'account_kit'
    ID_KEY = 'id'
    REQUIRES_EMAIL_VALIDATION = False
    EXTRA_DATA = ['cell_phone']

    def uses_redirect(self):
        return False

    def auth_complete(self, *args, **kwargs):
        """Completes login process, must return user instance"""
        key, secret = self.get_key_and_secret()
        access_token = self.get_access_token(key, secret, self.data['code'])

        cell_phone, details = self.get_account_details(secret, access_token)

        kwargs.update(
            {
               'username': cell_phone,
               'response': details,
               'backend': self
            }
        )
        return self.strategy.authenticate(*args, **kwargs)

    def request(self, url, method='GET', *args, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs.setdefault('timeout', self.setting('REQUESTS_TIMEOUT') or
                                     self.setting('URLOPEN_TIMEOUT'))

        if self.SEND_USER_AGENT and 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = user_agent()

        try:
            response = request(method, url, *args, **kwargs)
        except ConnectionError as err:
            raise AuthFailed(self, str(err))
        response.raise_for_status()
        return response

    def get_user_details(self, response):
        """Must return user details in a know internal struct:
            {'username': <username if any>,
             'email': <user email if any>,
             'fullname': <user full name if any>,
             'first_name': <user first name if any>,
             'last_name': <user last name if any>}
        """
        return {
            'cell_phone': response['phone']['number'].strip('+'),
            'cell_phone_is_valid': True}

    def get_json(self, url, *args, **kwargs):
        return self.request(url, *args, **kwargs).json()


    def auth_html(self):
        """Must return login HTML content returned by provider"""
        key, secret = self.get_key_and_secret()
        context = {'facebook_app_id': key}
        response = self.strategy.render_html(
            tpl='registration/account_kit_login.html', context=context
        )
        return response

    def start(self):
        return super().start()
