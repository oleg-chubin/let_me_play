from django.test import TestCase
from django.test.utils import override_settings
from let_me_escort.tasks import mytask


class AddTestCase(TestCase):

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_mytask(self):
        a = 1
        b = 4
        result = mytask.delay(a, b)
        self.assertTrue(result.get(), a + b)
        self.assertTrue(result.successful())
