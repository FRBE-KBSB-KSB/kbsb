# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from reddevil.core import get_secret

log = logging.getLogger(__name__)


def get_drive_service():
    """
    get Google drive service with delegated credentials of me myself and I
    this is dangerous, needs imrpovement
    """
    if not hasattr(get_drive_service, "service"):
        secret = get_secret("gdrive")
        cr = service_account.Credentials.from_service_account_info(
            secret, scopes=["https://www.googleapis.com/auth/drive"]
        )
        delegated_credentials = cr.with_subject("ruben.decrop@frbe-kbsb-ksb.be")
        get_drive_service.service = build(
            "drive", "v3", credentials=delegated_credentials
        )
    return get_drive_service.service
