# copyright Ruben Decrop 2012 - 2024
import logging
from . import MailRelayValidator
from reddevil.mail import MailParams
from reddevil.mail.mail import sendPlainEmail
from reddevil.core import get_settings

logger = logging.getLogger("kbsb")


async def mail_relay(mrv: MailRelayValidator):
    """
    sends an email, received from old site

    :param mrv: Description
    :type mrv: MailRelayValidator
    """
    settings = get_settings()
    mp = MailParams(
        receiver=mrv.receiver,
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL.get("bcc", ""),
        template=mrv.content,
        locale=None,
        subject=mrv.subject,
    )
    try:
        sendPlainEmail(mp)
    except Exception:
        logger.exception("failed")
