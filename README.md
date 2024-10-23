# django-gov-notify, a GOV.UK Notify flavoured Django email backend

![GitHub workflow](https://github.com/nimasmi/django-gov-notify/actions/workflows/CI-tests.yml/badge.svg)

django-gov-notify provides Django integration with the [GOV.UK Notify](https://www.notifications.service.gov.uk/) service for sending emails and SMS messages. [Python Client Documentation](https://docs.notifications.service.gov.uk/python.html).

This is implemented as a custom Django email backend. It presents a similar internal API to standard Django email backends, but with some restrictions:

- GOV.UK Notify emails are sent to one recipient each. CC: and BCC: fields are not supported.
- A single email 'message' with multiple recipients will result in multiple individual API calls to GOV.UK Notify, each message being sent to a single recipient. The backend will still report back `1`, as per Django's default behaviour.
- Attachments are not (at the moment) supported.
- Custom headers are not supported.
- To configure a 'reply-to' address, you must first configure such an address in the GOV.UK Notify admin interface.
- The 'from' address field is not supported. This must be configured within the GOV.UK Notify admin interface.
- Preformatted emails are expected to be configured in the service admin dashboard as Markdown templates with placeholders.
- The email body is interpreted as very limited Markdown. On testing, it seems that variables are not interpreted as markdown, or maybe mangled, e.g. `_test_` was emailed as `*test*`.

## Compatibility

django-gov-notify supports:

- Python 3.9, 3.10, 3.11 and 3.12
- Django 4.2, 5.0 and 5.1

## Installation

Using [pip](https://pip.pypa.io/en/stable/):

```bash
$ pip install django-gov-notify
```

Using [Poetry](https://python-poetry.org/)

```bash
$ poetry add django-gov-notify
```

## Configuration

In your Django project's settings:

```python
EMAIL_BACKEND = "django_gov_notify.backends.NotifyEmailBackend"
```

You will need at least one email template ID, with a plain template:

> Subject: ((subject))  
> Body: ((body))

Set the Django settings:

- `GOVUK_NOTIFY_API_KEY` (NB _not_ GOV_UK…)
- `GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID`

This plain template ID setting, and template IDs passed to the NotifyEmailMessage class, use string representations of the UUID keys.

## Usage

### Sending an email using a template

Configure the template in the [GOV.UK Notify dashboard](https://www.notifications.service.gov.uk/):

> Subject: Message about ((topic))  
> Body: Hello ((first name)), your reference is ((ref number))

Create an email message, supplying the template ID and a `personalisation` dictionary (this should also include any variables defined in the template subject):

```python
from django_gov_notify.message import NotifyEmailMessage

message = NotifyEmailMessage(
    to=["recipient@example.com"],
    template_id="43573f75-80e7-402f-b308-e5f1066fbd6f",
    personalisation={
        "topic": "The Prisoner",
        "first name": "Patrick",
        "ref number": "6",
    },
)
message.send()
```

Note that in this case a subject and body are not required, nor permitted, because the personalisation dict won't know how to do anything with them.

### Sending an email using the default (blank) template

This assumes you have configured a blank template with the parameters

> Subject: ((subject))  
> Body: ((body))

```python
from django_gov_notify.message import NotifyEmailMessage

message = NotifyEmailMessage(
    subject="Test subject", body="Test message content", to=["recipient@example.com"]
)
message.send()
```

Note that in this case a subject and body are required, and you must not pass the `template_id` or `personalisation` kwargs.

### Sending an email using the `send_mail` shortcut function

Use it in the normal fashion, including a 'from' address that will be discarded:

```python
from django.utils.mail import send_mail

send_mail("Subject", "Message content", "from@example.com", ["recipient@example.com"])
```

This will use the blank template ID configured as `settings.GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID`. Attachments, custom headers, and BCC recipients are not supported.

## Contributing

To work on this repository locally:

- install: `poetry install`
- run tests: `poetry run python runtests.py`
