"""
The tournament registrations proxy forwards only the path shapes the frontend
calls (SEC-32): the proxy adds the master-scoped key, so anything broader is
the whole dataplatform API. The OpenPairings and native SWAR file exports
are two more such shapes, and must not open anything else.
"""

import pytest
from fastapi import HTTPException

from kbsb.tournament_registrations.api_tournament_registrations import (
    TARGET_BASE_URL,
    _proxied_url,
)


@pytest.mark.parametrize(
    "path",
    [
        "admin/tournaments/42/export/openpairings",
        "admin/tournaments/42/export/swarfile",
        "admin/tournaments/42/export/csv",
        "admin/tournaments/42/export/swar/all",
        "admin/tournaments/42/registrations",
        # A team of a team tournament, and the admin's edit/delete of one.
        "42/teams",
        "admin/teams/7",
    ],
)
def test_frontend_shapes_are_forwarded(path):
    assert _proxied_url(path) == f"{TARGET_BASE_URL}/{path}"


@pytest.mark.parametrize(
    "path",
    [
        "admin/tournaments/42/export/openpairings/x",
        "admin/tournaments/42/export/openpairings/..",
        "admin/tournaments/../export/openpairings",
        "admin/tournaments/42/../../../players_fide/export/openpairings",
        "admin/tournaments/42/export/openpairings%2F..",
        "admin/tournaments/42/export/../../../players_fide",
        "admin/tournaments/42/export",
        "admin/tournaments/42/export/openpairingsx",
        "../players_fide/export/openpairings",
        "admin/tournaments/42/export/swarfile/x",
        "admin/tournaments/42/export/swarfile/..",
        "admin/tournaments/../export/swarfile",
        "admin/tournaments/42/../../../players_fide/export/swarfile",
        "admin/tournaments/42/export/swarfile%2F..",
        "admin/tournaments/42/export/swarfilex",
        "admin/tournaments/42/export/swarfile.swar",
        "../players_fide/export/swarfile",
        "42/teams/x",
        "42/teams/..",
        "../teams",
        "admin/teams/7/x",
        "admin/teams/..",
        "admin/teams/../tournaments",
        "admin/teams/7%2F..",
    ],
)
def test_anything_else_is_refused(path):
    with pytest.raises(HTTPException) as exc:
        _proxied_url(path)
    assert exc.value.status_code == 404


def test_the_visitor_address_is_sent_and_cannot_be_forged(monkeypatch):
    """
    The API counts limits per visitor, and every request arrives from Google's
    address, so the proxy names the visitor. A browser cannot pick the name.
    """
    import httpx
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from kbsb.tournament_registrations import api_tournament_registrations as mod

    seen = []
    real_client = httpx.AsyncClient

    def fake_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(
            lambda r: seen.append(r) or httpx.Response(200, json={})
        )
        return real_client(*args, **kwargs)

    monkeypatch.setattr(mod, "get_api_key", lambda: "the-key")
    monkeypatch.setattr(mod.httpx, "AsyncClient", fake_client)
    app = FastAPI()
    app.include_router(mod.router)
    client = TestClient(app)
    url = f"{mod.router.prefix}/admin/tournaments/42/registrations"

    client.get(
        url,
        headers={"x-appengine-user-ip": "203.0.113.7", "x-kbsb-visitor-ip": "1.2.3.4"},
    )
    client.get(url, headers={"x-kbsb-visitor-ip": "1.2.3.4"})

    assert seen[0].headers["x-kbsb-visitor-ip"] == "203.0.113.7"
    assert seen[1].headers["x-kbsb-visitor-ip"] == "testclient"
    assert seen[0].headers["x-api-key"] == "the-key"
