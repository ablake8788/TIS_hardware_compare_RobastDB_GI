"""
Adapter: implements ports.emailer.EmailerPort using smtplib.
Reads SMTP settings from AppSettings (loaded from tis_gap_app.ini).
Anti-corruption layer — translates internal EmailMessage to SMTP.
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from ports.emailer import EmailerPort, EmailMessage

logger = logging.getLogger(__name__)


class SMTPEmailer(EmailerPort):
    """Concrete SMTP email sender."""

    def __init__(self, smtp_server: str, smtp_port: int,
                 smtp_user: str, smtp_password: str):
        self._server   = smtp_server
        self._port     = smtp_port
        self._user     = smtp_user
        self._password = smtp_password

    def send(self, message: EmailMessage) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"]    = message.from_addr
            msg["To"]      = ", ".join(message.to)

            # Plain text + HTML parts
            msg.attach(MIMEText(message.body_text, "plain"))
            msg.attach(MIMEText(message.body_html, "html"))

            # Attachments (e.g. .docx report)
            if message.attachments:
                for filepath in message.attachments:
                    if filepath and os.path.isfile(filepath):
                        with open(filepath, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(filepath)}"
                        )
                        msg.attach(part)

            # Send via SMTP with TLS
            with smtplib.SMTP(self._server, self._port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self._user, self._password)
                server.sendmail(
                    message.from_addr,
                    message.to,
                    msg.as_string()
                )

            logger.info(f"Email sent to {message.to} — subject: {message.subject}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False
