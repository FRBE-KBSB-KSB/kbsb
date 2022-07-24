# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

from kbsb.main import app
from markdown2 import Markdown

# from reddevil.service.mail import sendEmail, MailParams
from reddevil.service.mail import MailParams
from reddevil.service.mailbackend import backends
from reddevil.common import get_settings
from jinja2 import FileSystemLoader, Environment, exceptions
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from pathlib import Path

log = logging.getLogger(__name__)
md = Markdown(extras=["tables"])


def get_template_env():
    if not hasattr(get_template_env, "env"):
        settings = get_settings()
        get_template_env.env = Environment(
            loader=FileSystemLoader(settings.TEMPLATES_PATH), trim_blocks=True
        )
    log.debug(f"jinja2 searchpath {get_template_env.env.loader.searchpath}")
    return get_template_env.env


def sendEmailNoAttachments(mp: MailParams, context: dict, name: str = ""):
    """
    sends an email with no attachment
    """
    settings = get_settings()
    env = get_template_env()
    try:
        tmpl = env.get_template(mp.template.format(locale=context["locale"]))
    except exceptions.TemplateNotFound as e:
        log.info(f"could not find template in searchpath {env.loader.searchpath}")
        raise e
    markdowntext = tmpl.render(**context)
    htmltext = md.convert(markdowntext)
    try:
        msg = MIMEMultipart("related")
        msg["Subject"] = mp.subject
        msg["From"] = mp.sender
        msg["To"] = mp.receiver
        if mp.cc:
            msg["Cc"] = mp.cc
        if mp.bcc:
            msg["Bcc"] = mp.bcc
        msg.preamble = "This is a multi-part message in MIME format."
        msgAlternative = MIMEMultipart("alternative")
        msgText = MIMEText(markdowntext)
        msgAlternative.attach(msgText)
        msgText = MIMEText(htmltext, "html")
        msgAlternative.attach(msgText)
        msg.attach(msgAlternative)
        backend = backends[settings.EMAIL["backend"]]()
        backend.send_message(msg)
        log.info(f"email {name} sent to {mp.receiver}")
    except Exception:
        log.exception("failed")


@app.post("/api/v1/testmail")
async def api_test_mail():
    mp = MailParams(
        locale="nl",
        receiver="ruben@decrop.net,ruben.decrop@bycco.be",
        cc="ruben@kosk.be,ruben@chessdevil.net",
        bcc="ruben.kbsb@gmail.com",
        sender="noreply@frbe-kbsb-ksb.be",
        subject="TestMail2",
        template="test/test_nl.md",
    )
    sendEmailNoAttachments(mp, {"locale": "nl"}, "testmail")
