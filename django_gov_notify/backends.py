import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address

from notifications_python_client.notifications import NotificationsAPIClient

from django_gov_notify.utils import cast_to_notify_email_message


class NotifyEmailBackend(BaseEmailBackend):
    """A Django email backend that works with the GOV.UK Notify service."""

    def __init__(self, *args, **kwargs):
        self._lock = threading.RLock()
        self.client = None
        self.api_key = kwargs.get("govuk_notify_api_key", settings.GOVUK_NOTIFY_API_KEY)
        super().__init__(*args, **kwargs)

    def open(self):
        if self.client:
            return
        self.client = NotificationsAPIClient(self.api_key)

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email messages
        sent.

        The GOV.UK Notify service requires one API request per recipient, and does not
        support CC or BCC addresses. Nonetheless the number returned by this method
        adheres to Django's default assumption of one email with multiple recipients
        equalling one "message" sent.
        """
        if not email_messages:
            return 0

        email_messages = [
            cast_to_notify_email_message(email_message, self.fail_silently)
            for email_message in email_messages
        ]

        if not email_messages:
            return 0

        with self._lock:
            self.open()
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False

        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        recipients = [
            sanitize_address(addr, encoding) for addr in email_message.recipients()
        ]
        message = email_message.message()
        try:
            for recipient in recipients:
                self.client.send_email_notification(email_address=recipient, **message)
        except Exception:
            if not self.fail_silently:
                raise
            return False
        return True
