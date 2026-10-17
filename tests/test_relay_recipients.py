import asyncio
import base64

import pytest
from reddevil.core import RdBadRequest

from kbsb.oldsite import oldsite
from kbsb.oldsite.md_oldsite import MailRelayValidator


def _mrv(receiver):
    return MailRelayValidator(
        content="x", receiver=receiver, sender="noreply@frbe-kbsb-ksb.be", subject="s"
    )


@pytest.mark.parametrize(
    "receiver",
    [
        "fide@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com",  # SWAR results to FIDE
        "ratings@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com",  # SWAR results to FRBE
        "Le666.echecs@gmail.com,ruben.kbsb@gmail.com",  # SWAR test
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


def _att(name, data):
    from reddevil.mail import MailAttachment

    return MailAttachment(
        filename=name,
        mimetype="application/octet-stream",
        content_base64=base64.b64encode(data).decode(),
    )


def _capture(monkeypatch):
    kept = {}
    monkeypatch.setattr(
        oldsite,
        "write_bucket_content",
        lambda path, f: kept.__setitem__(path, f.read()),
    )
    return kept


def test_a_report_is_kept_even_when_the_mail_fails(monkeypatch):
    kept = _capture(monkeypatch)

    def broken(mp):
        raise RuntimeError("gmail down")

    monkeypatch.setattr(oldsite, "sendEmailMessage", broken)
    mrv = _mrv("fide@frbe-kbsb-ksb.be,ruben.kbsb@gmail.com")
    mrv.attachments = [_att("S_FIDE_123_Open_20261017.txt", b"012 Open\n")]
    asyncio.run(oldsite.mail_relay(mrv))
    [(path, content)] = kept.items()
    assert path.startswith("oldsite_relay/") and path.endswith(
        "_0_S_FIDE_123_Open_20261017.txt"
    )
    assert content == b"012 Open\n"


def test_a_refused_mail_keeps_its_file_too(monkeypatch):
    kept = _capture(monkeypatch)
    monkeypatch.setattr(oldsite, "sendEmailMessage", lambda mp: None)
    mrv = _mrv("someone@example.com")
    mrv.attachments = [_att("x.txt", b"x")]
    with pytest.raises(RdBadRequest):
        asyncio.run(oldsite.mail_relay(mrv))
    assert len(kept) == 1


def test_a_filename_cannot_leave_the_folder(monkeypatch):
    kept = _capture(monkeypatch)
    monkeypatch.setattr(oldsite, "sendEmailMessage", lambda mp: None)
    mrv = _mrv("fide@frbe-kbsb-ksb.be")
    mrv.attachments = [_att("../../etc/passwd", b"x")]
    asyncio.run(oldsite.mail_relay(mrv))
    [path] = kept
    assert ".." not in path.split("/") and path.endswith("_passwd")


def test_a_storage_failure_does_not_stop_the_mail(monkeypatch):
    def broken(path, f):
        raise RuntimeError("bucket down")

    sent = []
    monkeypatch.setattr(oldsite, "write_bucket_content", broken)
    monkeypatch.setattr(oldsite, "sendEmailMessage", lambda mp: sent.append(mp))
    mrv = _mrv("fide@frbe-kbsb-ksb.be")
    mrv.attachments = [_att("x.txt", b"x")]
    asyncio.run(oldsite.mail_relay(mrv))
    assert len(sent) == 1
