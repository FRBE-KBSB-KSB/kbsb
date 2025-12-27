# copyright Ruben Decrop 2012 - 2024
# copyright Chessdevil Consulting BVBA 2015 - 2022

# we are using pydantic models (and not dicts) to represent
# to represent business obejcts

from pydantic import BaseModel
from reddevil.mail import MailAttachment


class MailRelayValidator(BaseModel):
    """
    Validator for incoming mail requests from old site
    """

    bcc: str = ""
    cc: str = ""
    attachments: list[MailAttachment] = None
    content: str
    receiver: str
    sender: str
    subject: str
