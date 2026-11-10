import asyncio

import pytest
from reddevil.core import RdBadRequest

from kbsb.oldsite import oldsite
from kbsb.oldsite.md_oldsite import MailRelayValidator


def _mrv(receiver):
    return MailRelayValidator(content="x", receiver=receiver, sender="noreply@frbe-kbsb-ksb.be", subject="s")


@pytest.mark.parametrize(
    "receiver",
    [
        "fide@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com",  # SWAR results to FIDE
        "ratings@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com",  # SWAR results to FRBE
        "Le666.echecs@gmail.com,ruben.kbsb@gmail.com",  # SWAR test
        "fide@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com,autoratingfide@frbe-kbsb-ksb.be",  # SWAR results, copied to the automation mailbox
        "fide@frbe-kbsb-ksb.be",  # FIDE Elo report
        " FIDE@frbe-kbsb-ksb.be ; Ruben <ruben.kbsb@gmail.com> ",
    ],
)
def test_what_the_old_site_sends_is_allowed(receiver):
    oldsite.check_recipients(receiver)


@pytest.mark.parametrize(
    "receiver",
    [
        "someone@example.com",
        "fide@frbe-kbsb-ksb.be,someone@example.com",
        "fide@frbe-kbsb-ksb.be.example.com",
        "",
        " , ",
    ],
)
def test_anything_else_is_refused(receiver):
    with pytest.raises(RdBadRequest):
        oldsite.check_recipients(receiver)


def test_a_refused_mail_is_never_sent(monkeypatch):
    sent = []
    monkeypatch.setattr(oldsite, "sendEmailMessage", lambda mp: sent.append(mp))
    with pytest.raises(RdBadRequest):
        asyncio.run(oldsite.mail_relay(_mrv("someone@example.com")))
    assert sent == []


def test_an_allowed_mail_is_sent(monkeypatch):
    sent = []
    monkeypatch.setattr(oldsite, "sendEmailMessage", lambda mp: sent.append(mp))
    asyncio.run(oldsite.mail_relay(_mrv("fide@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com")))
    assert len(sent) == 1
    assert sent[0].receiver == "fide@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com"
