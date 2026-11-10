# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2026

import sys
from datetime import UTC, datetime

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from reddevil.core import RdNotAuthorized, get_setting

from kbsb.core.tokens import get_salt, validate_token
from kbsb.member.login import superuser_login


def _secret(monkeypatch, value):
    login_module = sys.modules["kbsb.member.login"]
    monkeypatch.setattr(login_module, "get_secret", lambda name: value)


@pytest.mark.asyncio
async def test_superuser_login_success():
    # Uses test-superuser.json configured in tests/settings.py
    token = await superuser_login("SU__test", "test-password")
    assert isinstance(token, str)

    jwt_settings = get_setting("JWT")
    token_settings = get_setting("TOKEN")
    claims = jwt.decode(
        token,
        jwt_settings["secret"] + get_salt(),
        algorithms=[jwt_settings["algorithm"]],
    )
    assert claims["sub"] == "SU__test"
    now_ts = datetime.now(tz=UTC).timestamp()
    expected_exp = now_ts + (token_settings["timeout"] * 60)
    assert abs(claims["exp"] - expected_exp) < 10

    # Token verifies for admin routes
    auth = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert await validate_token(auth) == "SU__test"


@pytest.mark.asyncio
async def test_superuser_login_with_mocked_secret(monkeypatch):
    _secret(monkeypatch, {"SU__custom": "custom-password"})
    token = await superuser_login("SU__custom", "custom-password")
    assert isinstance(token, str)

    auth = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert await validate_token(auth) == "SU__custom"


@pytest.mark.asyncio
async def test_superuser_login_wrong_password():
    with pytest.raises(RdNotAuthorized) as exc_info:
        await superuser_login("SU__test", "wrong-password")
    assert exc_info.value.description == "WrongUsernamePasswordCombination"


@pytest.mark.asyncio
async def test_superuser_login_unknown_superuser():
    with pytest.raises(RdNotAuthorized) as exc_info:
        await superuser_login("SU__unknown", "test-password")
    assert exc_info.value.description == "WrongUsernamePasswordCombination"


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_secret", [None, "", b"", [], "not-a-dict"])
async def test_superuser_login_invalid_secret(monkeypatch, bad_secret):
    _secret(monkeypatch, bad_secret)
    with pytest.raises(RdNotAuthorized) as exc_info:
        await superuser_login("SU__test", "test-password")
    assert exc_info.value.description == "WrongUsernamePasswordCombination"


@pytest.mark.asyncio
async def test_superuser_login_secret_manager_error(monkeypatch):
    def _failing_get_secret(name):
        raise RuntimeError("Secret Manager unavailable")

    login_module = sys.modules["kbsb.member.login"]
    monkeypatch.setattr(login_module, "get_secret", _failing_get_secret)
    with pytest.raises(RdNotAuthorized) as exc_info:
        await superuser_login("SU__test", "test-password")
    assert exc_info.value.description == "WrongUsernamePasswordCombination"
