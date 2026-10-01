"""
Cloudflare Turnstile on the FIDE registration form (kbsb.fide.turnstile).

Turnstile is on only when both the site key and the secret key are there;
otherwise the submit works as before and Cloudflare is never called. When on,
a submit goes through only when Cloudflare accepts the token for our hostname
and action; when Cloudflare cannot be reached, the submit is refused.

Cloudflare is never reached from here: httpx is replaced by a fake. For a
manual test, Cloudflare's test keys (see kbsb.fide.turnstile) are
  secret 1x0000000000000000000000000000000AA (passes),
  secret 2x0000000000000000000000000000000AA (fails),
  site key 1x00000000000000000000AA (passes), 2x00000000000000000000AB (blocks).
"""

import json
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from reddevil.core import get_settings

from kbsb.fide import api_fide, turnstile
from kbsb.main import app

T = json.loads(
    (Path(__file__).parents[1] / "src/kbsb/fide/translations.json").read_text(encoding="utf-8")
)
MSG = T["en"]["messages"]

SITEKEY = "1x00000000000000000000AA"
SECRET = "1x0000000000000000000000000000000AA"
# what validate_form answers in these tests: reaching it means the submit got
# past Turnstile into the normal processing (and stops there, before mailing)
REACHED = "reached validate_form"


class FakeAsyncClient:
    """Stands in for httpx.AsyncClient; records the siteverify calls."""

    calls = []
    answer = None  # a dict, or an exception to raise

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, data=None, **kwargs):
        FakeAsyncClient.calls.append({"url": url, "data": data, "timeout": self.kwargs.get("timeout")})
        if isinstance(FakeAsyncClient.answer, Exception):
            raise FakeAsyncClient.answer
        return httpx.Response(
            200,
            json=FakeAsyncClient.answer,
            request=httpx.Request("POST", url),
        )


@pytest.fixture
def cloudflare(monkeypatch):
    FakeAsyncClient.calls = []
    FakeAsyncClient.answer = {
        "success": True,
        "hostname": "www.frbe-kbsb-ksb.be",
        "action": "fide_registration",
    }
    monkeypatch.setattr(turnstile, "httpx", SimpleNamespace(AsyncClient=FakeAsyncClient))
    return FakeAsyncClient


@pytest.fixture
def stop_at_validation(monkeypatch):
    monkeypatch.setattr(api_fide, "validate_form", lambda form, lang: [REACHED])
    sent = []
    monkeypatch.setattr(api_fide, "sendEmailMessage", lambda params: sent.append(params))
    return sent


def configure(monkeypatch, sitekey="", secret=""):
    monkeypatch.setattr(get_settings(), "TURNSTILE_SITEKEY", sitekey, raising=False)
    if secret:
        monkeypatch.setenv("TURNSTILE_SECRET", secret)
    else:
        monkeypatch.delenv("TURNSTILE_SECRET", raising=False)
    monkeypatch.setattr(turnstile, "_secret_cache", {"value": None, "failed_at": 0.0})


@pytest.fixture
def on(monkeypatch):
    configure(monkeypatch, SITEKEY, SECRET)


def submit(token=None, locale="en", headers=None):
    body = {"formdata": {"event_name": "Test Open"}}
    if token is not None:
        body["turnstile_token"] = token
    client = TestClient(app)
    return client.post(f"/api/v1/fide/generate?locale={locale}", json=body, headers=headers or {})


def assert_reached(response):
    assert response.status_code == 400
    assert response.json()["errors"] == [REACHED]
    assert "x-fide-error" not in response.headers


def assert_refused(response, key, status=400, locale="en"):
    assert response.status_code == status
    assert response.headers["x-fide-error"] == key
    assert response.json()["errors"] == [T[locale]["messages"][key]]


# off


@pytest.mark.parametrize(
    "sitekey,secret",
    [("", ""), (SITEKEY, ""), ("", SECRET)],
    ids=["nothing", "no secret", "no site key"],
)
def test_off_submit_is_as_before(monkeypatch, cloudflare, stop_at_validation, sitekey, secret):
    configure(monkeypatch, sitekey, secret)
    assert_reached(submit())
    assert_reached(submit(token="anything"))
    assert cloudflare.calls == []


@pytest.mark.parametrize(
    "sitekey,secret",
    [("", ""), (SITEKEY, ""), ("", SECRET)],
    ids=["nothing", "no secret", "no site key"],
)
def test_off_form_data_has_no_site_key(monkeypatch, sitekey, secret):
    configure(monkeypatch, sitekey, secret)
    data = TestClient(app).get("/api/v1/fide/form-data").json()
    assert data["turnstile_sitekey"] == ""
    assert "translations" in data and "lookups" in data


def test_secret_manager_failure_keeps_it_off(monkeypatch, cloudflare, stop_at_validation):
    configure(monkeypatch, SITEKEY)

    def broken():
        raise RuntimeError("no access")

    monkeypatch.setattr(turnstile, "_read_secret", broken)
    assert turnstile.is_enabled() is False
    assert_reached(submit())
    assert cloudflare.calls == []


# on


def test_on_form_data_gives_the_site_key(on):
    data = TestClient(app).get("/api/v1/fide/form-data").json()
    assert data["turnstile_sitekey"] == SITEKEY


@pytest.mark.parametrize("token", [None, "", "   "])
def test_missing_token_is_refused(on, cloudflare, stop_at_validation, token):
    assert_refused(submit(token=token), turnstile.MSG_REQUIRED)
    assert cloudflare.calls == []


def test_accepted_token_goes_through(on, cloudflare, stop_at_validation):
    response = submit(token="good-token", headers={"X-Appengine-User-IP": "203.0.113.7"})
    assert_reached(response)
    assert len(cloudflare.calls) == 1
    call = cloudflare.calls[0]
    assert call["url"] == "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    assert call["data"] == {"secret": SECRET, "response": "good-token", "remoteip": "203.0.113.7"}
    assert call["timeout"] == 10.0


def test_bare_domain_is_accepted(on, cloudflare, stop_at_validation):
    cloudflare.answer["hostname"] = "frbe-kbsb-ksb.be"
    assert_reached(submit(token="good-token"))


def test_remoteip_falls_back_to_the_client(on, cloudflare, stop_at_validation):
    submit(token="good-token")
    assert cloudflare.calls[0]["data"]["remoteip"] == "testclient"


@pytest.mark.parametrize(
    "answer",
    [
        {"success": True, "hostname": "evil.example", "action": "fide_registration"},
        {"success": True, "hostname": "www.frbe-kbsb-ksb.be", "action": "login"},
        {"success": True, "hostname": "www.frbe-kbsb-ksb.be"},
        {"success": False, "error-codes": ["invalid-input-response"]},
        {"success": "true", "hostname": "www.frbe-kbsb-ksb.be", "action": "fide_registration"},
    ],
    ids=["wrong hostname", "wrong action", "no action", "success false", "success not a bool"],
)
def test_bad_answers_are_refused(on, cloudflare, stop_at_validation, answer):
    cloudflare.answer = answer
    response = submit(token="some-token")
    assert_refused(response, turnstile.MSG_FAILED)
    assert stop_at_validation == []


def test_localhost_only_in_dev_modes(on, cloudflare, stop_at_validation, monkeypatch):
    cloudflare.answer["hostname"] = "localhost"
    assert_reached(submit(token="good-token"))
    monkeypatch.setattr(turnstile, "is_dev_mode", lambda: False)
    assert_refused(submit(token="good-token"), turnstile.MSG_FAILED)


@pytest.mark.parametrize(
    "error",
    [httpx.ConnectError("down"), httpx.ReadTimeout("slow"), RuntimeError("network access blocked")],
    ids=["connect", "timeout", "other"],
)
def test_unreachable_cloudflare_is_refused(on, cloudflare, stop_at_validation, error):
    cloudflare.answer = error
    response = submit(token="some-token")
    assert_refused(response, turnstile.MSG_UNAVAILABLE, status=503)
    assert stop_at_validation == []


@pytest.mark.parametrize("locale", ["en", "nl", "fr"])
def test_refusals_are_translated(on, cloudflare, stop_at_validation, locale):
    assert_refused(submit(locale=locale), turnstile.MSG_REQUIRED, locale=locale)
    cloudflare.answer = {"success": False}
    assert_refused(submit(token="t", locale=locale), turnstile.MSG_FAILED, locale=locale)
    cloudflare.answer = httpx.ConnectError("down")
    assert_refused(submit(token="t", locale=locale), turnstile.MSG_UNAVAILABLE, 503, locale)


def test_messages_exist_in_every_language():
    for lang in ("en", "nl", "fr"):
        assert T[lang]["ui"]["turnstile_hint"]
        for key in (turnstile.MSG_REQUIRED, turnstile.MSG_FAILED, turnstile.MSG_UNAVAILABLE):
            assert T[lang]["messages"][key], (lang, key)


def test_secret_is_read_once(monkeypatch):
    configure(monkeypatch, SITEKEY)
    reads = []

    def read():
        reads.append(1)
        return SECRET

    monkeypatch.setattr(turnstile, "_read_secret", read)
    assert turnstile.is_enabled() and turnstile.is_enabled()
    assert len(reads) == 1


def test_secret_is_not_read_without_a_site_key(monkeypatch):
    configure(monkeypatch)
    monkeypatch.setattr(turnstile, "_read_secret", lambda: pytest.fail("secret read"))
    assert turnstile.is_enabled() is False
