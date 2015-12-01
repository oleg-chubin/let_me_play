from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core import signing


def send_validation(strategy, backend, code):
    signature = signing.dumps({"session_key": strategy.session.session_key, "email": code.email},
                              key=settings.EMAIL_SECRET_KEY)
    url = "{0}?verification_code={1}&signature={2}".format(
        reverse('social:complete', args=(backend.name,)),
        code.code, signature)
    url = strategy.request.build_absolute_uri(url)
    send_mail('Validate your account', 'Validate your account {0}'.format(url),
              settings.EMAIL_FROM, [code.email], fail_silently=False)
