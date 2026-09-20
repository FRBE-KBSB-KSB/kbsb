# copyright Ruben Decrop 2012 - 2024
import logging
from asyncio import sleep

from reddevil.core import get_setting
from reddevil.mail import MailParams
from reddevil.mail.mail import sendEmailMessage

from . import MailRelayValidator

logger = logging.getLogger("kbsb")


async def mail_relay(mrv: MailRelayValidator):
    """
    sends an email, received from old site

    :param mrv: Description
    :type mrv: MailRelayValidator
    """
    email_settings = get_setting("EMAIL")
    mp = MailParams(
        receiver=mrv.receiver,
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=email_settings.get("bcc", ""),
        template=mrv.content,
        locale="",
        subject=mrv.subject,
        attachments=mrv.attachments or [],
    )
    try:
        sendEmailMessage(mp)
        await sleep(0)
    except Exception:
        logger.exception("failed")
