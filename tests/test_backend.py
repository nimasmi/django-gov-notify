from unittest import mock

from django.conf import settings
from django.core.mail import send_mail
from django.test import TestCase, override_settings

from django_gov_notify.backends import NotifyEmailBackend
from django_gov_notify.message import NotifyEmailMessage
from tests.fixtures import NotifyEmailMessageFactory


@mock.patch("django_gov_notify.backends.NotificationsAPIClient")
class EmailBackendTest(TestCase):
    def setUp(self):
        self.backend = NotifyEmailBackend(govuk_notify_api_key="not a real key")

    @override_settings(
        GOVUK_NOTIFY_API_KEY="fake settings key"  # pragma: allowlist secret
    )
    def test_default_key(self, mock_client):
        backend = NotifyEmailBackend()
        self.assertEqual(backend.api_key, "fake settings key")
        message = NotifyEmailMessageFactory()
        backend.send_messages([message])
        mock_client.assert_has_calls([mock.call("fake settings key")])

    def test_creating_with_non_standard_key(self, mock_client):
        fake_key = "fake positional arg key"
        backend = NotifyEmailBackend(govuk_notify_api_key=fake_key)
        self.assertEqual(backend.api_key, fake_key)
        message = NotifyEmailMessageFactory()
        backend.send_messages([message])
        mock_client.assert_has_calls([mock.call(fake_key)])

    def test_we_can_send_notify_message_without_subject_or_body(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"],
            template_id="43573f75-80e7-402f-b308-e5f1066fbd6f",
            personalisation={"foo": "bar"},
        )
        self.assertEqual(message.send(), 1)

    def test_we_can_send_notify_message_with_template_but_no_personalisation(
        self, mock_client
    ):
        """Test for using a template which does not have any variables"""
        message = NotifyEmailMessage(
            to=["recipient@example.com"],
            template_id="43573f75-80e7-402f-b308-e5f1066fbd6f",
        )
        self.assertEqual(message.send(), 1)

    def test_we_can_send_notify_message_with_only_subject_and_body(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"], subject="Subject", body="Message content"
        )
        self.assertEqual(message.send(), 1)

    def test_subject_without_body_is_not_allowed(self, mock_client):
        message = NotifyEmailMessage(to=["recipient@example.com"], subject="Subject")
        with self.assertRaises(ValueError):
            message.send()

    def test_body_without_subject_is_not_allowed(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"], body="Message content"
        )
        with self.assertRaises(ValueError):
            message.send()

    def test_subject_not_permitted_with_custom_template(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"],
            subject="Subject",
            template_id="43573f75-80e7-402f-b308-e5f1066fbd6f",
            personalisation={"foo": "bar"},
        )
        with self.assertRaises(ValueError):
            message.send()

    def test_body_not_permitted_with_custom_template(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"],
            body="Message content",
            template_id="43573f75-80e7-402f-b308-e5f1066fbd6f",
            personalisation={"foo": "bar"},
        )
        with self.assertRaises(ValueError):
            message.send()

    def test_personalisation_without_template_id_is_not_allowed(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"], personalisation={"foo": "bar"}
        )
        with self.assertRaises(ValueError):
            message.send()

    def test_template_id_not_permitted_with_subject_and_body(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"],
            subject="Subject",
            body="Message content",
            template_id="43573f75-80e7-402f-b308-e5f1066fbd6f",
        )
        with self.assertRaises(ValueError):
            message.send()

    def test_personalisation_not_permitted_with_subject_and_body(self, mock_client):
        message = NotifyEmailMessage(
            to=["recipient@example.com"],
            subject="Subject",
            body="Message content",
            personalisation={"foo": "bar"},
        )
        with self.assertRaises(ValueError):
            message.send()


@mock.patch("django_gov_notify.backends.NotificationsAPIClient")
@override_settings(
    EMAIL_BACKEND="django_gov_notify.backends.NotifyEmailBackend",
    GOVUK_NOTIFY_API_KEY="not_a_real_key",  # pragma: allowlist secret
)
class DjangoInternalEmailAPITest(TestCase):
    """Tests of the django.core.send_mail function with the Notifications Backend"""

    def send_mail(self, **kwargs):
        options = {
            "subject": "Test Subject",
            "body": "Test body content",
            "from_email": "webmaster@example.com",
            "to": ["user@example.com"],
        }
        options.update(kwargs)
        return send_mail(
            options["subject"], options["body"], options["from_email"], options["to"]
        )

    def test_send_mail(self, mock_client):
        try:
            self.send_mail()
        except Exception:
            self.fail("django.core.mail.send_mail raised an exception unexpectedly")

    def test_send_mail_uses_notify_backend(self, mock_client):
        self.send_mail()
        mock_client().send_email_notification.assert_called_once()

    def test_send_mail_sends_to_correct_recipient(self, mock_client):
        recipients = ["recipient@example.com"]
        self.send_mail(to=recipients)
        mock_client().send_email_notification.assert_called_once()
        name, args, kwargs = mock_client().send_email_notification.mock_calls[0]
        self.assertEqual(kwargs["email_address"], recipients[0])

    def test_send_mail_to_multiple_recipients_results_in_multiple_calls(
        self, mock_client
    ):
        recipients = ["recipient1@example.com", "recipient2@example.com"]
        self.send_mail(to=recipients)
        mock_client().send_email_notification.assert_has_calls(
            [
                mock.call(
                    email_address="recipient1@example.com",
                    template_id=mock.ANY,
                    personalisation=mock.ANY,
                ),
                mock.call(
                    email_address="recipient2@example.com",
                    template_id=mock.ANY,
                    personalisation=mock.ANY,
                ),
            ]
        )

    def test_send_mail_comes_from_default_reply_to_address(self, mock_client):
        """Tests thath the email_reply_to_id kwarg is not supplied."""
        self.send_mail()
        mock_client().send_email_notification.assert_called_once()
        name, args, kwargs = mock_client().send_email_notification.mock_calls[0]
        self.assertNotIn("email_reply_to_id", kwargs)

    def test_send_mail_uses_plain_template(self, mock_client):
        subject = "This is the test subject"
        body = "This is the email content\nRegards\nTester"
        self.send_mail(subject=subject, body=body)
        mock_client().send_email_notification.assert_called_once_with(
            email_address=mock.ANY,
            template_id=settings.GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID,
            personalisation={"subject": subject, "body": body},
        )

    def test_send_mail_reports_number_sent(self, mock_client):
        self.assertEqual(self.send_mail(), 1)
        mock_client.reset_mock()
        self.assertEqual(self.send_mail(to=["a@example.com", "b@example.com"]), 1)
        # …even though two emails have been sent
        self.assertEqual(len(mock_client().send_email_notification.mock_calls), 2)
