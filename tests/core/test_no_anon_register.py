"""
reddevil's /api/v1/accounts/anon/register would let any visitor create an
enabled admin account. The site takes it off the router in main.py; the
other account routes (login, the admin's account management) stay.
"""

from fastapi.testclient import TestClient
from reddevil.account import api_account

from kbsb.main import app

REGISTER = "/api/v1/accounts/anon/register"


def _paths():
    return {getattr(r, "path", None) for r in api_account.router.routes}


def test_the_register_route_is_gone():
    assert REGISTER not in _paths()


def test_posting_to_it_finds_nothing():
    client = TestClient(app)
    reply = client.post(
        REGISTER,
        json={
            "email": "someone@example.be",
            "id": "someone@example.be",
            "password": "x" * 12,
        },
    )
    assert reply.status_code in (404, 405)


def test_login_and_account_management_stay():
    paths = _paths()
    assert "/api/v1/accounts/anon/login" in paths
    assert "/api/v1/accounts/mgmt/account" in paths
    client = TestClient(app)
    assert client.post("/api/v1/accounts/anon/login", json={}).status_code != 404
