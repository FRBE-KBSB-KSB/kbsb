# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

from kbsb.main import app
from reddevil.service.mail import sendEmail, MailParams


@app.post("/api/v1/testmail")
async def api_test_mail():
    mp = MailParams(
        locale="nl",
        receiver="ruben@decrop.net,ruben.decrop@bycco.be",
        sender="noreply@frbe-kbsb-ksb.be",
        subject="TestMail",
        template="interclub/enrollment_{locale}.md",
    )
    sendEmail(mp, {"locale": "nl"}, "testmail")
