"""
Superuser logins are limited after repeated failures, and a disabled admin
account's token is refused.
"""

import sys
from types import SimpleNamespace

import pytest
from reddevil.core import RdNotAuthorized

from kbsb.core import loginlimit, tokens
from kbsb.member.login import superuser_login


class FakeCollection:
    """Just enough of a MongoDB collection for the limiter."""

    def __init__(self):
        self.docs = []

    async def create_index(self, *args, **kwargs):
        return None

    async def insert_many(self, docs):
        self.docs.extend(dict(d) for d in docs)
        return SimpleNamespace(inserted_ids=list(range(len(docs))))

    async def count_documents(self, query):
        since = query["ts"]["$gte"]
        return sum(1 for d in self.docs if d["key"] == query["key"] and d["ts"] >= since)


@pytest.fixture
def failures(monkeypatch):
    coll = FakeCollection()
    monkeypatch.setattr(loginlimit, "_collection", lambda: coll)
    monkeypatch.setitem(loginlimit._index, "done", False)
    login_module = sys.modules["kbsb.member.login"]
    monkeypatch.setattr(login_module, "get_secret", lambda name: {"SU__test": "right"})
    return coll


@pytest.mark.asyncio
async def test_the_right_password_logs_in(failures):
    assert isinstance(await superuser_login("SU__test", "right", "1.2.3.4"), str)
    assert failures.docs == []


@pytest.mark.asyncio
async def test_a_wrong_password_is_counted(failures):
    with pytest.raises(RdNotAuthorized):
        await superuser_login("SU__test", "wrong", "1.2.3.4")
    assert len(failures.docs) == 2  # one for the name, one for the IP


@pytest.mark.asyncio
async def test_a_name_is_locked_after_five_failures(failures):
    for i in range(loginlimit.NAME_MAX):
        with pytest.raises(RdNotAuthorized):
            await superuser_login("SU__test", "wrong", f"10.0.0.{i}")
    # even the right password, from yet another IP, now waits
    with pytest.raises(loginlimit.TooManyLoginAttempts) as e:
        await superuser_login("SU__test", "right", "10.0.0.99")
    assert e.value.status_code == 429


@pytest.mark.asyncio
async def test_an_ip_is_locked_after_twenty_failures(failures):
    for i in range(loginlimit.IP_MAX):
        with pytest.raises(RdNotAuthorized):
            await superuser_login(f"SU__guess{i}", "wrong", "6.6.6.6")
    with pytest.raises(loginlimit.TooManyLoginAttempts):
        await superuser_login("SU__test", "right", "6.6.6.6")
    # another IP is not affected
    assert isinstance(await superuser_login("SU__test", "right", "7.7.7.7"), str)


@pytest.mark.asyncio
async def test_without_mongodb_the_login_still_works(monkeypatch):
    def broken():
        raise RuntimeError("MongoDB is not connected")

    monkeypatch.setattr(loginlimit, "_collection", broken)
    login_module = sys.modules["kbsb.member.login"]
    monkeypatch.setattr(login_module, "get_secret", lambda name: {"SU__test": "right"})
    assert isinstance(await superuser_login("SU__test", "right", "1.2.3.4"), str)


@pytest.mark.asyncio
async def test_an_unknown_name_is_refused(failures):
    with pytest.raises(RdNotAuthorized):
        await superuser_login("SU__nobody", "right", "1.2.3.4")


# disabled admin accounts


def _db(monkeypatch, account):
    from reddevil.account import DbAccount
    from reddevil.core import RdNotFound

    async def find_single(options):
        if account is None:
            raise RdNotFound()
        return account

    monkeypatch.setattr(DbAccount, "find_single", find_single)


@pytest.mark.asyncio
async def test_an_enabled_account_has_its_salt(monkeypatch):
    _db(monkeypatch, {"tokensalt": "s1", "enabled": True})
    assert await tokens.get_tokensalt("admin@frbe-kbsb-ksb.be") == "s1"


@pytest.mark.asyncio
async def test_a_disabled_account_has_no_salt(monkeypatch):
    _db(monkeypatch, {"tokensalt": "s1", "enabled": False})
    assert await tokens.get_tokensalt("admin@frbe-kbsb-ksb.be") is None


@pytest.mark.asyncio
async def test_an_account_without_the_flag_has_no_salt(monkeypatch):
    _db(monkeypatch, {"tokensalt": "s1"})
    assert await tokens.get_tokensalt("admin@frbe-kbsb-ksb.be") is None


@pytest.mark.asyncio
async def test_an_unknown_account_has_no_salt(monkeypatch):
    _db(monkeypatch, None)
    assert await tokens.get_tokensalt("nobody@example.be") is None
