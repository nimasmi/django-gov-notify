import uuid

from django.test import TestCase, override_settings

from django_gov_notify.message import NotifyEmailMessage
from tests.fixtures import NotifyEmailMessageFactory


class EmailMessageTest(TestCase):
    def test_basic(self):
        try:
            NotifyEmailMessage(subject="Test Subject", body="Test body content")
        except Exception:
            self.fail("Creating email message raised an exception unexpectedly.")

    def test_using_factory(self):
        try:
            NotifyEmailMessageFactory()
        except Exception:
            self.fail(
                "Creating email message from factory raised an exception unexpectedly."
            )

    def test_creating_with_one_recipient(self):
        try:
            NotifyEmailMessageFactory(to=["user@example.com"])
        except Exception:
            self.fail(
                "Creating email message with one recipient raised an exception unexpectedly."
            )

    def test_creating_with_multiple_recipients(self):
        try:
            NotifyEmailMessageFactory(
                to=["user@example.com", "another.user@example.com"]
            )
        except Exception:
            self.fail(
                "Creating email message with one recipient raised an exception unexpectedly."
            )

    def test_from_email_not_permitted(self):
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(from_email="webmaster@example.com")

    def test_attachments_not_permitted(self):
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(attachments=[("foo.txt", "Foo", "text/plain")])

    def test_custom_headers_not_permitted(self):
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(headers={"foo": "bar"})

    def test_cc_not_permitted(self):
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(cc=["webmaster@example.com"])

    def test_bcc_not_permitted(self):
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(bcc=["webmaster@example.com"])

    def test_attaching_not_permitted(self):
        email_message = NotifyEmailMessageFactory()
        with self.assertRaises(TypeError):
            email_message.attach("foo.txt", "Foo", "text/plain")

    def test_attaching_file_not_permitted(self):
        email_message = NotifyEmailMessageFactory()
        with self.assertRaises(TypeError):
            email_message.attach_file("foo.txt")

    def test_message_dict(self):
        message = NotifyEmailMessageFactory().message()
        self.assertIsInstance(message, dict)

    def test_default_subject_if_template_id_not_supplied(self):
        email_message = NotifyEmailMessageFactory()
        message = email_message.message()
        self.assertEqual(message["personalisation"]["subject"], email_message.subject)

    def test_default_body_if_template_id_not_supplied(self):
        email_message = NotifyEmailMessageFactory()
        message = email_message.message()
        self.assertEqual(message["personalisation"]["body"], email_message.body)

    def test_default_template_id_used_if_not_supplied(self):
        template_id = str(uuid.uuid4())
        with override_settings(GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID=template_id):
            message = NotifyEmailMessageFactory().message()
        self.assertEqual(message["template_id"], template_id)

    def test_custom_template_id(self):
        custom_template_id = str(uuid.uuid4())
        message = NotifyEmailMessageFactory(
            subject=None,
            body=None,
            template_id=custom_template_id,
            personalisation={"foo": "bar"},
        ).message()
        self.assertEqual(message["template_id"], custom_template_id)

    def test_bad_template_id(self):
        bad_template_id = "foo"
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(template_id=bad_template_id)

    def test_uuid_template_id(self):
        uuid_template_id = uuid.uuid4()
        with self.assertRaises(TypeError):
            NotifyEmailMessageFactory(template_id=uuid_template_id)

    def test_email_reply_to_id_is_used_if_not_supplied(self):
        message = NotifyEmailMessageFactory().message()
        self.assertNotIn("email_reply_to_id", message)

    def test_custom_email_reply_to_id(self):
        custom_email_reply_to_id = str(uuid.uuid4())
        message = NotifyEmailMessageFactory(
            email_reply_to_id=custom_email_reply_to_id
        ).message()
        self.assertEqual(message["email_reply_to_id"], custom_email_reply_to_id)

    def test_bad_email_reply_to_id(self):
        bad_email_reply_to_id = "foo"
        with self.assertRaises(ValueError):
            NotifyEmailMessageFactory(email_reply_to_id=bad_email_reply_to_id)

    def test_uuid_email_reply_to_id(self):
        uuid_email_reply_to_id = uuid.uuid4()
        with self.assertRaises(TypeError):
            NotifyEmailMessageFactory(email_reply_to_id=uuid_email_reply_to_id)
