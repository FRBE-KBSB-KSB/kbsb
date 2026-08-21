# copyright Ruben Decrop 2012 - 2021
# copyright Chessdevil Consulting BVBA 2015 - 2020

# this file is written by Ruben Decrop, and is derived from source code
# written by Chessdevil Consulting BVBA
# This file can only be used as is for the frbe-kbsb-ksb.be website
# for any other use a written agreement is required by Chessdevil Consulting

import logging
from markdown2 import Markdown
from io import BytesIO
from typing import List, Any
import os.path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from kbsb import settings

# from kbsb.models.md_book100 import Book100Optional

from .mailbackend import backends

log = logging.getLogger(__name__)
md = Markdown()


def test_mail():
    """
    send a test mail
    """
    try:
        sender = settings.EMAIL["sender"]
        receiver = "ruben.decrop@gmail.com"
        msg = MIMEMultipart("relate1")
        msg["Subject"] = "Testmail 2"
        msg["From"] = sender
        msg["To"] = receiver
        if settings.EMAIL.get("blindcopy"):
            msg["Bcc"] = settings.EMAIL["blindcopy"]
        msg.preamble = "This is a multi-part message in MIME format."
        msgAlternative = MIMEMultipart("alternative")
        msgText = MIMEText("Hi it is I Leclercq, I am in disguise")
        msgAlternative.attach(msgText)
        msgText = MIMEText("Hi, It is I <b>Leclercq</b> I am in disguise", "html")
        msgAlternative.attach(msgText)
        msg.attach(msgAlternative)
        backend = backends[settings.EMAIL["backend"]]()
        backend.send_message(msg)
        log.info(f"testmail sent for {receiver}")
    except Exception:
        log.exception("failed")
