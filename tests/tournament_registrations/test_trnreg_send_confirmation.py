"""
/send-confirmation relays a mail for the dataplatform, gated by the secret the
two share. An empty secret must never open it, and the send itself runs off
the event loop.
"""

import pytest
from fastapi.testclient import TestClient

from kbsb.main import app
from kbsb.tournament_registrations import api_tournament_registrations as trn

URL = "/api/v1/tournament_registrations/send-confirmation"
PAYLOAD = {"subject": "Bevestiging", "html": "<p>x</p>", "to": ["a@example.be"]}


@pytest.fixture
def sent(monkeypatch):
    mails = []
    monkeypatch.setattr(trn, "sendEmailMessage", lambda params: mails.append(params))
    monkeypatch.setattr(
        trn, "get_mail_setting", lambda name: {"account": "noreply@example.be"}
    )
    return mails


@pytest.mark.parametrize("presented", [None, ""])
def test_an_empty_secret_does_not_open_the_relay(monkeypatch, sent, presented):
    monkeypatch.setattr(trn, "get_mail_bridge_secret", lambda: "")
    headers = {} if presented is None else {"x-mail-bridge-secret": presented}
    r = TestClient(app).post(URL, json=PAYLOAD, headers=headers)
    assert r.status_code == 401
    assert sent == []


def test_a_wrong_secret_is_refused(monkeypatch, sent):
    monkeypatch.setattr(trn, "get_mail_bridge_secret", lambda: "s3cret")
    r = TestClient(app).post(URL, json=PAYLOAD, headers={"x-mail-bridge-secret": "x"})
    assert r.status_code == 401
    assert sent == []


def test_the_right_secret_sends(monkeypatch, sent):
    monkeypatch.setattr(trn, "get_mail_bridge_secret", lambda: "s3cret")
    r = TestClient(app).post(
        URL, json=PAYLOAD, headers={"x-mail-bridge-secret": "s3cret"}
    )
    assert r.status_code == 200, r.text
    assert [m.receiver for m in sent] == ["a@example.be"]


def test_the_send_runs_off_the_event_loop(monkeypatch, sent):
    import asyncio

    def send(params):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            sent.append("off the loop")
        else:
            sent.append("on the loop")

    monkeypatch.setattr(trn, "sendEmailMessage", send)
    monkeypatch.setattr(trn, "get_mail_bridge_secret", lambda: "s3cret")
    r = TestClient(app).post(
        URL, json=PAYLOAD, headers={"x-mail-bridge-secret": "s3cret"}
    )
    assert r.status_code == 200, r.text
    assert sent == ["off the loop"]
