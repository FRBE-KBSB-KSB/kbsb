"""
The FIDE form only sends text and tick boxes. A hand-made submit with a list,
an object or a number in a field is a 400, not a 500, and mails nothing.
"""

import pytest
from fastapi.testclient import TestClient
from reddevil.core import get_settings

from kbsb.fide import api_fide, ratelimit, turnstile
from kbsb.main import app


@pytest.fixture
def sent(monkeypatch):
    monkeypatch.setattr(get_settings(), "TURNSTILE_SITEKEY", "", raising=False)
    monkeypatch.setattr(turnstile, "_secret_cache", {"value": None, "failed_at": 0.0})
    monkeypatch.setattr(ratelimit, "a_get_mongodb", lambda: None)
    mails = []
    monkeypatch.setattr(api_fide, "sendEmailMessage", lambda p: mails.append(p))
    return mails


def post(formdata):
    return TestClient(app).post(
        "/api/v1/fide/generate?locale=en", json={"formdata": formdata}
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("start_date", 20270308),
        ("end_date", ["2027-03-08"]),
        ("event_name", {"a": 1}),
        ("rounds_reported", [7]),
        ("expected_players", 60.5),
        ("homepage", ["x"]),
    ],
)
def test_a_field_that_is_not_text_is_a_400(sent, field, value):
    form = {"event_name": "Test Open", "start_date": "2027-03-08", field: value}
    r = post(form)
    assert r.status_code == 400
    assert r.json()["errors"] == [f"{field}: not a text value"]
    assert sent == []


@pytest.mark.parametrize("formdata", [["x"], "x", 5])
def test_formdata_that_is_not_an_object_is_a_400(sent, formdata):
    r = post(formdata)
    assert r.status_code == 400
    assert sent == []


def test_tick_boxes_and_empty_fields_are_fine(sent):
    form = {"event_name": "Test Open", "report_deadline_ack": True, "max_rating": None}
    assert api_fide.non_text_fields(form) == []


@pytest.mark.parametrize("value", [[1], {"a": 1}, object()])
def test_parse_int_refuses_what_is_not_a_number(value):
    errors = []
    assert api_fide.parse_int(value, "Rounds", errors, "en") is None
    assert len(errors) == 1
