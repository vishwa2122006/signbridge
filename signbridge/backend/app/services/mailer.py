"""Sends email over SMTP, e.g. Gmail with an app password (SMTP_USER and
SMTP_PASSWORD in backend/.env).

Without SMTP_PASSWORD nothing is sent: each message is logged instead, so
login codes still work on a local setup. The latest messages are kept in
`outbox` either way, which is how tests read them.
"""

import logging
import smtplib
import ssl
from collections import deque
from email.message import EmailMessage
from email.utils import formataddr
from typing import Iterable, Optional

from app import config

log = logging.getLogger(__name__)

outbox: deque = deque(maxlen=100)


class EmailError(RuntimeError):
    pass


def enabled() -> bool:
    return bool(config.SMTP_USER and config.SMTP_PASSWORD)


def send(to: Iterable[str], subject: str, text: str, html: Optional[str] = None):
    """Raises EmailError when SMTP is set up but the message can't be sent."""
    recipients = list(dict.fromkeys(address for address in to if address))
    if not recipients:
        return
    outbox.append({"to": recipients, "subject": subject, "text": text, "html": html})
    if not enabled():
        log.warning("Email NOT sent (set SMTP_USER and SMTP_PASSWORD in backend/.env)\nTo: %s\nSubject: %s\n\n%s",
                    ", ".join(recipients), subject, text)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((config.MAIL_FROM_NAME, config.MAIL_FROM))
    message["To"] = ", ".join(recipients)
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    try:
        if config.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=20, context=context) as smtp:
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as smtp:
                smtp.starttls(context=context)
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
                smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as e:
        log.error("Sending email %r to %s failed: %s", subject, ", ".join(recipients), e)
        raise EmailError(str(e)) from e


def send_quietly(to: Iterable[str], subject: str, text: str, html: Optional[str] = None):
    """For notifications: a failure is logged (by send) instead of raised."""
    try:
        send(to, subject, text, html)
    except EmailError:
        pass
