"""
The FIDE registration form must not be usable to make the federation mail
its workbook to any address (kbsb.fide.ratelimit), and nothing typed in the
form may reach a mail header with a line break in it.

Limits: per client IP at most IP_PER_HOUR submits an hour and IP_PER_DAY a
day, per address at most ADDRESS_PER_DAY confirmation mails a day, counted in
MongoDB. MongoDB is replaced by an in-memory fake here; mails are recorded,
never sent.
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from reddevil.core import get_settings
from zerotwocloud.mail import MailParams, ZcBadRequest
from zerotwocloud.mail import mail as zc_mail

from kbsb.fide import api_fide, ratelimit, turnstile
from kbsb.main import app

T = json.loads(
    (Path(__file__).parents[1] / "src/kbsb/fide/translations.json").read_text(encoding="utf-8")
)

IP = "203.0.113.7"
INVOICE = "club@example.be"
CONTACT = "organiser@example.be"


class FakeCollection:
    """The few pymongo calls ratelimit makes, over a list of documents."""

    def __init__(self):
        self.docs = []
        self.indexes = []

    async def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))

    async def count_documents(self, query):
        since = query["ts"]["$gte"]
        return sum(1 for d in self.docs if d["key"] == query["key"] and d["ts"] >= since)

    async def insert_many(self, docs):
        self.docs.extend(docs)

    def add(self, kind, value, n, age):
        ts = datetime.now(UTC) - age
        self.docs.extend({"key": ratelimit.hashed_key(kind, value), "ts": ts} for _ in range(n))


@pytest.fixture
def db(monkeypatch):
    coll = FakeCollection()
    monkeypatch.setattr(ratelimit, "a_get_mongodb", lambda: {ratelimit.COLLECTION: coll})
    monkeypatch.setattr(ratelimit, "_index", {"done": False})
    return coll


@pytest.fixture
def sent(monkeypatch):
    # Turnstile off: these tests are about what comes after it
    monkeypatch.setattr(get_settings(), "TURNSTILE_SITEKEY", "", raising=False)
    monkeypatch.setattr(turnstile, "_secret_cache", {"value": None, "failed_at": 0.0})
    mails = []
    monkeypatch.setattr(api_fide, "sendEmailMessage", lambda params: mails.append(params))
    return mails


def valid_form(**extra):
    form = {
        "invoice_email": INVOICE,
        "invoice_clubnr": "601",
        "national_championship_143a": "No",
        "on_fide_calendar": "Yes",
        "tournament_report": "All rounds in 1 report",
        "tournament_type": "Individual",
        "event_name": "Brussels Open 2027",
        "city": "Brussels",
        "country": "BEL",
        "expected_players": "60",
        "tournament_system": "Swiss",
        "rounds_reported": "7",
        "female_only": "No",
        "start_date": "2027-03-08",
        "end_date": "2027-03-12",
        "title_norms": "No",
        "gm_wgm_norms": "No",
        "chief_arbiter_name": "Arbiter, Chief",
        "chief_arbiter_fide_id": "200000",
        "chief_organizer_name": "Organiser, Chief",
        "chief_organizer_fide_id": "200001",
        "time_control_code": "Standard",
        "time_control_desc": "90min/40moves+30min/end+30sec/move from move 1",
        "all_digital_clocks": "Yes",
        "tiebreak_method": "Buchholz",
        "software": "Swiss Manager",
        "contact_email": CONTACT,
        "homepage": "https://example.be",
        "communication_language": "en",
    }
    form.update(extra)
    return form


def submit(form=None, ip=IP, locale="en"):
    client = TestClient(app)
    headers = {"X-Appengine-User-IP": ip} if ip else {}
    return client.post(
        f"/api/v1/fide/generate?locale={locale}",
        json={"formdata": form or valid_form()},
        headers=headers,
    )


def assert_limited(response, locale="en"):
    assert response.status_code == 429
    assert response.headers["x-fide-error"] == ratelimit.MSG_RATE_LIMITED
    assert response.json()["errors"] == [T[locale]["messages"]["rate_limited"]]


# the limits


def test_a_valid_submit_goes_through_and_is_counted(db, sent):
    r = submit()
    assert r.status_code == 200, r.text
    # fide@ and the two confirmation copies
    assert [m.receiver for m in sent] == [api_fide.FIDE_MAILBOX, INVOICE, CONTACT]
    keys = {d["key"] for d in db.docs}
    assert keys == {
        ratelimit.hashed_key("ip", IP),
        ratelimit.hashed_key("mail", INVOICE),
        ratelimit.hashed_key("mail", CONTACT),
    }
    # stored hashed: no IP or address in the collection
    assert IP not in str(db.docs) and INVOICE not in str(db.docs)
    # the TTL index
    assert ("ts", {"expireAfterSeconds": int(ratelimit.KEEP.total_seconds())}) in db.indexes


def test_ip_hourly_limit(db, sent):
    for i in range(ratelimit.IP_PER_HOUR):
        # other addresses each time, so only the IP limit can be reached
        form = valid_form(invoice_email=f"club{i}@example.be", contact_email=f"org{i}@example.be")
        assert submit(form).status_code == 200
    n = len(sent)
    r = submit(valid_form(invoice_email="new@example.be", contact_email="new2@example.be"))
    assert_limited(r)
    assert len(sent) == n  # nothing mailed
    # another IP is not affected
    other = valid_form(invoice_email="new@example.be", contact_email="new2@example.be")
    assert submit(other, ip="198.51.100.1").status_code == 200


def test_ip_daily_limit(db, sent):
    db.add("ip", IP, ratelimit.IP_PER_DAY - 1, timedelta(hours=3))
    assert submit().status_code == 200
    r = submit(valid_form(invoice_email="new@example.be", contact_email="new2@example.be"))
    assert_limited(r)


def test_old_submits_no_longer_count(db, sent):
    db.add("ip", IP, ratelimit.IP_PER_DAY, timedelta(hours=25))
    db.add("mail", CONTACT, ratelimit.ADDRESS_PER_DAY, timedelta(hours=25))
    assert submit().status_code == 200


def test_address_daily_limit(db, sent):
    # the address is the limit here, from any IP, in any case
    db.add("mail", CONTACT, ratelimit.ADDRESS_PER_DAY, timedelta(hours=2))
    r = submit(valid_form(contact_email=CONTACT.upper()), ip="198.51.100.9")
    assert_limited(r)
    assert sent == []
    # a refused submit is not counted
    assert ratelimit.hashed_key("ip", "198.51.100.9") not in {d["key"] for d in db.docs}


def test_address_just_under_the_limit(db, sent):
    db.add("mail", CONTACT, ratelimit.ADDRESS_PER_DAY - 1, timedelta(hours=2))
    assert submit().status_code == 200
    assert_limited(submit(ip="198.51.100.9"))


@pytest.mark.parametrize("locale", ["en", "nl", "fr"])
def test_refusal_is_translated(db, sent, locale):
    db.add("ip", IP, ratelimit.IP_PER_HOUR, timedelta(minutes=5))
    assert_limited(submit(locale=locale), locale)


def test_invalid_form_is_not_counted(db, sent):
    r = submit(valid_form(city=""))
    assert r.status_code == 400
    assert db.docs == []


def test_internal_test_address_has_only_the_ip_limit(db, sent):
    db.add("mail", api_fide.INTERNAL_TEST_ADDRESS, 50, timedelta(hours=1))
    r = submit(valid_form(invoice_email="JORIAN.INTERNAL", contact_email="JORIAN.INTERNAL"))
    assert r.status_code == 200, r.text
    assert {d["key"] for d in db.docs if d["ts"] > datetime.now(UTC) - timedelta(minutes=1)} == {
        ratelimit.hashed_key("ip", IP)
    }


def test_client_host_without_the_app_engine_header(db, sent):
    assert submit(ip=None).status_code == 200
    assert ratelimit.hashed_key("ip", "testclient") in {d["key"] for d in db.docs}


def test_mongodb_down_lets_the_submit_through(monkeypatch, sent):
    monkeypatch.setattr(ratelimit, "a_get_mongodb", lambda: None)
    monkeypatch.setattr(ratelimit, "_index", {"done": False})
    assert submit().status_code == 200
    assert len(sent) == 3


def test_messages_exist_in_every_language():
    for lang in ("en", "nl", "fr"):
        for key in ("rate_limited", "invalid_email"):
            assert T[lang]["messages"][key]


# mail headers


@pytest.mark.parametrize(
    "address",
    [
        "club@example.be\r\nBcc: victim@example.com",
        "club@example.be\nBcc: victim@example.com",
        "club@example.be, victim@example.com",
        "club@example.be;victim@example.com",
        "Club <club@example.be>",
        "club @example.be",
        "not-an-address",
    ],
)
@pytest.mark.parametrize("field", ["invoice_email", "contact_email"])
def test_header_addresses_are_single_plain_addresses(db, sent, field, address):
    r = submit(valid_form(**{field: address}))
    assert r.status_code == 400
    message = T["en"]["messages"]["invalid_email"]
    assert any(e.endswith(message) for e in r.json()["errors"])
    assert sent == []
    assert db.docs == []


@pytest.mark.parametrize("address", ["first.last@example.be", "a+fide@sub.example.be"])
def test_normal_addresses_are_accepted(db, sent, address):
    assert submit(valid_form(contact_email=address)).status_code == 200


def test_event_name_with_a_line_break_is_refused(db, sent):
    r = submit(valid_form(event_name="Open\r\nBcc: victim@example.com"))
    assert r.status_code == 400
    assert sent == []


def test_headers_of_the_sent_mails_have_no_line_breaks(db, sent):
    assert submit(valid_form(contact_email=f"  {CONTACT}  ")).status_code == 200
    for m in sent:
        for value in (m.subject, m.receiver, m.reply_to, m.bcc, m.cc, m.sender):
            assert "\r" not in value and "\n" not in value
    assert sent[0].reply_to == CONTACT
    assert sent[2].receiver == CONTACT


def test_the_form_mails_through_zerotwocloud():
    # the library that refuses a line break in a header, as tested below
    from zerotwocloud.mail.mail import sendEmailMessage

    assert api_fide.sendEmailMessage is sendEmailMessage


@pytest.mark.parametrize("header", ["subject", "receiver", "reply_to"])
def test_zerotwocloud_refuses_a_line_break_in_a_header(monkeypatch, header):
    monkeypatch.setattr(zc_mail, "_send", lambda msg: pytest.fail("mail sent"))
    params = dict(
        locale="en",
        receiver="club@example.be",
        sender="noreply@example.be",
        subject="Open",
        template="<p>x</p>",
        reply_to="fide@example.be",
    )
    params[header] = params[header] + "\r\nBcc: victim@example.com"
    with pytest.raises(ZcBadRequest):
        zc_mail.sendEmailMessage(MailParams(**params))
