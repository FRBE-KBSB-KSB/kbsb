# copyright Ruben Decrop 2012 - 2024
import logging
from asyncio import sleep

from reddevil.core import RdBadRequest, get_setting
from reddevil.mail import MailParams
from reddevil.mail.mail import sendEmailMessage

from . import MailRelayValidator

logger = logging.getLogger("kbsb")

# The only addresses the old site mails in practice. SWAR sends its results to
# fide@ or ratings@ with a copy to Ruben and to the rating automation mailbox,
# or to its own test address; the club and player scripts copy admin@. Anything else is refused, so the relay key
# alone cannot be used to mail members or anyone else from noreply@.
ALLOWED_RECIPIENTS = {
    "fide@frbe-kbsb-ksb.be",
    "ratings@frbe-kbsb-ksb.be",
    "admin@frbe-kbsb-ksb.be",
    "autoratingfide@frbe-kbsb-ksb.be",
    "ruben.kbsb@gmail.com",
    "le666.echecs@gmail.com",
}


def recipients(receiver: str) -> list[str]:
    "the addresses in a receiver string: comma or semicolon separated, 'Name <addr>' allowed"
    found = []
    for part in receiver.replace(";", ",").split(","):
        part = part.strip()
        if "<" in part and part.endswith(">"):
            part = part[part.rindex("<") + 1 : -1].strip()
        if part:
            found.append(part.lower())
    return found


def check_recipients(receiver: str) -> None:
    addresses = recipients(receiver or "")
    refused = [a for a in addresses if a not in ALLOWED_RECIPIENTS]
    if not addresses or refused:
        logger.warning(f"mail relay refused, recipients not allowed: {refused or 'none given'}")
        raise RdBadRequest(description="RecipientNotAllowed")


async def mail_relay(mrv: MailRelayValidator):
    """
    sends an email, received from old site

    :param mrv: Description
    :type mrv: MailRelayValidator
    """
    check_recipients(mrv.receiver)
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
