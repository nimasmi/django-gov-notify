from django.test import TestCase

from django_gov_notify import __version__


class DjangoGOVNotifyTest(TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.1.0")
