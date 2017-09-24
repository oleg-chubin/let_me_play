"""
Legacy Email backend, docs at:
    http://psa.matiasaguirre.net/docs/backends/email.html
"""
from social.backends.legacy import LegacyAuth


class SmsAuth(LegacyAuth):
    name = 'sms'
    ID_KEY = 'cell_phone'
    REQUIRES_EMAIL_VALIDATION = False
    EXTRA_DATA = ['cell_phone']
