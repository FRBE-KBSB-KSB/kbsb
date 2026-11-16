"""
reddevil's account routes (/api/v1/accounts/mgmt/account...) manage the admin
accounts. reddevil's own validate_token never checks a token's signature, so
the site makes those routes use kbsb.core.tokens.validate_token: an unsigned,
alg=none or wrongly signed token is refused, a genuine admin token works.

The account store is replaced here; nothing reaches MongoDB.
"""

import base64
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from reddevil.account import api_account
from reddevil.core import get_setting

from kbsb.core import tokens
from kbsb.main import app

URL = "/api/v1/accounts/mgmt/account"
ADMIN = "admin@example.be"
ACCOUNT_SALT = "the-accounts-own-salt"
SECRET = get_setting("JWT")["secret"]
ALG = get_setting("JWT")["algorithm"]


def _b64(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def signed(sub=ADMIN, key=None, minutes=30):
    payload = {"sub": sub, "exp": datetime.now(tz=UTC) + timedelta(minutes=minutes)}
    return jwt.encode(payload, key or (SECRET + ACCOUNT_SALT), ALG)


FORGED = {
    "alg none": _b64({"alg": "none", "typ": "JWT"}) + "." + _b64({"sub": ADMIN}) + ".",
    "alg None": _b64({"alg": "None", "typ": "JWT"}) + "." + _b64({"sub": ADMIN}) + ".",
    "unsigned HS256": jwt.encode({"sub": ADMIN}, "", "HS256"),
    "signed with a guessed key": signed(key="guessed"),
    "signed without the account's salt": signed(key=SECRET),
    "expired": signed(minutes=-1),
    "superuser name, guessed key": signed(sub="SU__ruben", key="guessed"),
}


@pytest.fixture
def store(monkeypatch):
    calls = []

    async def get_tokensalt(sub):
        return ACCOUNT_SALT if sub == ADMIN else None

    monkeypatch.setattr(tokens, "get_tokensalt", get_tokensalt)
    monkeypatch.setattr(
        api_account, "get_accounts", AsyncMock(side_effect=lambda: calls.append("list") or [])
    )
    monkeypatch.setattr(
        api_account,
        "delete_account",
        AsyncMock(side_effect=lambda i: calls.append(("delete", i))),
    )
    return calls


@pytest.mark.parametrize("name", list(FORGED))
def test_a_forged_token_cannot_manage_accounts(store, name):
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {FORGED[name]}"}
    assert client.get(URL, headers=headers).status_code == 401
    assert client.delete(f"{URL}/someone", headers=headers).status_code == 401
    r = client.post(
        URL,
        headers=headers,
        json={"id": "evil@example.be", "email": "evil@example.be", "password": "x"},
    )
    assert r.status_code in (401, 422)
    assert store == []


def test_no_token_cannot_manage_accounts(store):
    assert TestClient(app).get(URL).status_code == 401
    assert store == []


def test_a_genuine_admin_token_still_works(store):
    headers = {"Authorization": f"Bearer {signed()}"}
    r = TestClient(app).get(URL, headers=headers)
    assert r.status_code == 200, r.text
    assert store == ["list"]


def test_the_account_routes_use_the_sites_validator():
    assert api_account.validate_token is tokens.validate_token
