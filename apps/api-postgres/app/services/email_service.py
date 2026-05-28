import smtplib
from email.mime.text import MIMEText

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EmailService:
    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASS
        self.use_tls = settings.SMTP_USE_TLS
        self.from_addr = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"

    def send(self, to_email: str, subject: str, body: str) -> None:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = to_email

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.user:
                    server.login(self.user, self.password)
                server.sendmail(settings.EMAIL_FROM, [to_email], msg.as_string())
            logger.info("email_enviado", to=to_email, subject=subject)
        except Exception as e:
            logger.error("erro_envio_email", to=to_email, erro=str(e))
            raise
