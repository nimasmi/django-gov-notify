from django.core.mail import EmailMessage
from django.test import TestCase

from django_gov_notify.backends import NotifyEmailBackend
from django_gov_notify.message import NotifyEmailMessage
from django_gov_notify.utils import cast_to_notify_email_message


class EmailBackendConversionTest(TestCase):
    def setUp(self):
        self.backend = NotifyEmailBackend(govuk_notify_api_key="not a real key")

    def test_convert_to_notify_message(self):
        message = EmailMessage(
            "Hello",
            "Body goes here",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
        )
        converted = cast_to_notify_email_message(message, self.backend.fail_silently)
        self.assertTrue(isinstance(converted, NotifyEmailMessage))

    def test_from_email_is_ignored(self):
        message = EmailMessage(
            "Hello",
            "Body goes here",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
        )
        self.assertEqual(message.from_email, "from@example.com")
        converted = cast_to_notify_email_message(message, self.backend.fail_silently)
        self.assertEqual(converted.from_email, None)

    def test_custom_headers_are_ignored(self):
        headers = {"Message-ID": "foo"}
        message = EmailMessage(
            "Hello",
            "Body goes here",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
            headers=headers,
        )
        self.assertEqual(message.extra_headers, headers)
        converted = cast_to_notify_email_message(message, self.backend.fail_silently)
        self.assertEqual(converted.extra_headers, {})

    def test_converting_with_attachments_not_permitted(self):
        attachments = [("foo.txt", "Foo", "text/plain")]
        message = EmailMessage(
            "Hello",
            "Body goes here",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
            reply_to=["another@example.com"],
            attachments=attachments,
        )
        self.assertEqual(message.attachments, attachments)
        with self.assertRaises(ValueError):
            cast_to_notify_email_message(message, self.backend.fail_silently)

    def test_converting_with_cc_addresses_not_permitted(self):
        cc = ["webmaster@example.com"]
        message = EmailMessage(
            "Hello",
            "Body goes here",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
            cc=cc,
        )
        self.assertEqual(message.cc, cc)
        with self.assertRaises(ValueError):
            cast_to_notify_email_message(message, self.backend.fail_silently)

    def test_converting_with_bcc_addresses_not_permitted(self):
        bcc = ["webmaster@example.com"]
        message = EmailMessage(
            "Hello",
            "Body goes here",
            "from@example.com",
            ["to1@example.com", "to2@example.com"],
            bcc=bcc,
        )
        self.assertEqual(message.bcc, bcc)
        with self.assertRaises(ValueError):
            cast_to_notify_email_message(message, self.backend.fail_silently)
