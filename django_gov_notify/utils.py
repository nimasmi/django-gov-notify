from django_gov_notify.message import NotifyEmailMessage


def cast_to_notify_email_message(email_message, fail_silently):
    """Converts an EmailMessage instance to a NotifyEmailMessage.

    We silently ignore from_email, headers, and reply_to kwargs, because these are
    inserted by default by the django.core.send_mail function. Other attributes are
    passed on.
    """
    if not isinstance(email_message, NotifyEmailMessage):
        try:
            email_message = NotifyEmailMessage(
                subject=email_message.subject,
                body=email_message.body,
                to=email_message.to,
                bcc=email_message.bcc,
                attachments=email_message.attachments,
                cc=email_message.cc,
            )
        except Exception:
            if not fail_silently:
                raise
    return email_message
