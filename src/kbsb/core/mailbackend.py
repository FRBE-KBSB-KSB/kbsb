#    Copyright 2019 Chessdevil Consulting

import base64
import logging
import smtplib
from email.mime.base import MIMEBase

from fastapi import HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build
from reddevil.core import get_setting

log = logging.getLogger(__name__)

cc = "book100@frbe-kbsb-ksb.be"


class BaseEmailBackend:
    def send_message(self, msg: MIMEBase) -> None:
        raise HTTPException(503, detail="EmailBackendNotImplemented")


class SmtpSslBackend(BaseEmailBackend):
    def send_message(self, msg: MIMEBase) -> None:
        email_settings = get_setting("EMAIL")
        with smtplib.SMTP_SSL(email_settings["host"], email_settings["port"]) as s:
            if email_settings.get("user"):
                s.login(email_settings["user"], email_settings["password"])
            s.send_message(msg)


class SmtpBackend(BaseEmailBackend):
    def send_message(self, msg: MIMEBase) -> None:
        email_settings = get_setting("EMAIL")
        with smtplib.SMTP(email_settings["host"], email_settings["port"]) as s:
            if email_settings.get("user"):
                s.login(email_settings["user"], email_settings["password"])
            s.send_message(msg)


class GmailBackend(BaseEmailBackend):
    def send_message(self, msg: MIMEBase) -> None:
        service = get_gmail_service()
        rmsg = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")}
        try:
            service.users().messages().send(userId="me", body=rmsg).execute()
        except Exception:
            log.exception("sending Gmail message failed")


def get_gmail_service():
    if not hasattr(get_gmail_service, "service"):
        email_settings = get_setting("EMAIL")
        try:
            credentials = service_account.Credentials.from_service_account_file(
                email_settings["serviceaccountfile"],
                scopes=["https://www.googleapis.com/auth/gmail.send"],
            )
            delegated_credentials = credentials.with_subject(email_settings["account"])
            service = build("gmail", "v1", credentials=delegated_credentials)
            get_gmail_service.service = service  # type: ignore
        except Exception:
            log.exception("Cannot setup Gmail API")
            raise HTTPException(503, detail="GmailAPINotAvailable")
    return get_gmail_service.service  # type: ignore


backends = {
    "SMTP": SmtpBackend,
    "SMTP_SSL": SmtpSslBackend,
    "GMAIL": GmailBackend,
}
