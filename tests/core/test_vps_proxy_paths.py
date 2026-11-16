"""
The players_fide, arbiters and national_elo_archive proxies add an API key
to every request, so they forward only the path shapes the frontend calls,
and none of the browser's own x-* headers. A free path was the whole
dataplatform API: "..%2F..%2Fplayers_national/..." left the proxy's scope.
"""

import httpx
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from kbsb.arbiters import api_arbiters
from kbsb.national_elo_archive import api_national_elo_archive
from kbsb.players_fide import api_players_fide

MODULES = {
    "players_fide": api_players_fide,
    "arbiters": api_arbiters,
    "national_elo_archive": api_national_elo_archive,
}

ALLOWED = {
    "players_fide": ["search", "12345"],
    "arbiters": ["search", "12345"],
    "national_elo_archive": [
        "search",
        "clubs",
        "clubs/all",
        "player/12345",
        "player/12345/games",
        "club/101/players",
    ],
}

REFUSED = [
    "",
    "..",
    "../players_national/1",
    "../../players_national/ratings.csv",
    "search/..",
    "search/../../players_national",
    "12345/../../players_national",
    "%2e%2e/players_national",
    "..%2Fplayers_national",
    "search.json",
    "search/x",
    "12 345",
    "12345\n",
    "player/../../players_national",
    "player/1/../../../players_national",
    "player/1/games/x",
    "club/1/players/..",
    "clubs/all/..",
]


@pytest.mark.parametrize(
    "name,path", [(n, p) for n, paths in ALLOWED.items() for p in paths]
)
def test_frontend_shapes_are_forwarded(name, path):
    mod = MODULES[name]
    assert mod._proxied_url(path) == f"{mod.TARGET_BASE_URL}/{path}"


@pytest.mark.parametrize("name", list(MODULES))
@pytest.mark.parametrize("path", REFUSED)
def test_anything_else_is_refused(name, path):
    with pytest.raises(HTTPException) as exc:
        MODULES[name]._proxied_url(path)
    assert exc.value.status_code == 404


@pytest.fixture
def upstream(monkeypatch):
    """Every module's outgoing requests, answered locally and recorded."""
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    real_client = httpx.AsyncClient

    def fake_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return real_client(*args, **kwargs)

    for mod in MODULES.values():
        monkeypatch.setattr(mod, "get_api_key", lambda: "the-key")
        monkeypatch.setattr(mod, "_client", None, raising=False)
        monkeypatch.setattr(mod.httpx, "AsyncClient", fake_client)
    return seen


def _client():
    app = FastAPI()
    for mod in MODULES.values():
        app.include_router(mod.router)
    return TestClient(app)


@pytest.mark.parametrize("name", list(MODULES))
def test_encoded_traversal_never_reaches_the_api(name, upstream):
    client = _client()
    for path in ("..%2F..%2Fplayers_national/x", "%2e%2e/%2e%2e/players_national"):
        r = client.get(f"/api/v1/{name}/{path}")
        assert r.status_code == 404
    assert upstream == []


@pytest.mark.parametrize("name", list(MODULES))
def test_browser_x_headers_are_not_forwarded(name, upstream):
    client = _client()
    r = client.get(
        f"/api/v1/{name}/search?q=x",
        headers={
            "x-archive-client-ip": "1.2.3.4",
            "x-api-key": "visitor",
            "x-forwarded-for": "5.6.7.8",
            "authorization": "Bearer abc",
            "cookie": "a=b",
            "accept-language": "nl",
        },
    )
    assert r.status_code == 200
    (sent,) = upstream
    assert str(sent.url) == f"{MODULES[name].TARGET_BASE_URL}/search?q=x"
    assert sent.headers["x-api-key"] == "the-key"
    assert sent.headers["accept-language"] == "nl"
    for h in ("x-forwarded-for", "authorization", "cookie"):
        assert h not in sent.headers
    # the archive proxy names the visitor itself; the others say nothing
    assert sent.headers.get("x-archive-client-ip") != "1.2.3.4"
