# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

import logging
import yaml
import os
import csv
from pathlib import Path
from jinja2 import Template, FileSystemLoader, Environment
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from reddevil.common import get_settings
from kbsb.service.secrets import get_secret

log = logging.getLogger(__name__)
settings = get_settings()
cwd = Path(".")
env = Environment(loader=FileSystemLoader(os.fspath(cwd / "frontend" / "templates")))


# google drive API
scopes = ["https://www.googleapis.com/auth/drive"]
_service = None


def get_drive_service():
    """
    get Google drive service with delegated credentials of me myself and I
    this is dangerous, needs imrpovement
    """
    if getattr(get_drive_service,"service"):
        secret = get_secret("kbsb-gdrive")
        cr = service_account.Credentials.from_service_account_info(secret, scopes=scopes)
        delegated_credentials = cr.with_subject("ruben.decrop@frbe-kbsb-ksb.be")
        setattr(get_drive_service, "service", build("drive", "v3", credentials=delegated_credentials)
    return get_drive_service.service


async def fetchI18n() -> None:
    request = (
        get_drive_service()
        .files()
        .export_media(fileId=settings.GOOGLEDRIVE_TRANSLATIONID, mimeType="text/csv")
    )
    with (cwd / "data" / "i18n.csv").open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    with (cwd / "data" / "i18n.csv").open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        allrows = []
        for r in reader:
            allrows.append(r)
    for l in ["en", "fr", "nl", "de"]:
        with (cwd / "frontend" / "lang" / f"{l}.js").open("w", encoding="utf8") as f:
            f.write("export default {\n")
            for r in allrows:
                f.write(f'"{r["key"]}": `{r[l]}`,\n')
            f.write("}\n")
