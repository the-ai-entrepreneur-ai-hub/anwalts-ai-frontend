import os
import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)


def send_email(subject: str, to_email: str, body_text: str) -> bool:
    """Send an email using SMTP settings from environment.
    If SMTP is not configured, logs the message and returns False.

    Env vars:
    - SMTP_HOST, SMTP_PORT (default 1025 for local dev like MailHog)
    - SMTP_USER, SMTP_PASSWORD (optional)
    - SMTP_TLS ("1" to enable STARTTLS)
    - SMTP_FROM (default no-reply@anwalts.ai)
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "1025"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_TLS", "0") == "1"
    from_email = os.getenv("SMTP_FROM", "no-reply@anwalts.ai")

    if not host:
        logger.warning("SMTP not configured; email content below:\nTo: %s\nSubject: %s\n%s", to_email, subject, body_text)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body_text)

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            if use_tls:
                try:
                    server.starttls()
                except Exception as e:
                    logger.warning("STARTTLS failed: %s", e)
            if user and password:
                server.login(user, password)
            server.send_message(msg)
        logger.info("Email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("SMTP send failed: %s", e)
        return False

