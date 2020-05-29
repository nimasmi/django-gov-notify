import factory

from django_gov_notify.message import NotifyEmailMessage


class NotifyEmailMessageFactory(factory.Factory):
    class Meta:
        model = NotifyEmailMessage

    subject = "Test Subject"
    body = "Test body content"
