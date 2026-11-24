"""
Club pages fetch their members' ratings in one keyed request, and fall back to
one request per member when the API refuses the batch.
"""

import asyncio

import httpx

from kbsb.core import eloserver


def _client(handler):
    return httpx.AsyncClient(
        base_url="https://api.test", transport=httpx.MockTransport(handler)
    )


def test_one_request_for_a_whole_club(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "ratings": {
                    "11": {"standard": 2010},
                    "12": {"standard": None},
                },
                "not_found": [13],
            },
        )

    monkeypatch.setattr(
        eloserver, "_get_eloserver_asynclient", lambda: _client(handler)
    )
    monkeypatch.setattr(eloserver, "eloserver_secret", "the-key")

    ratings = asyncio.run(eloserver.get_fideelos(iter([12, 11, False, 13, 11])))

    assert ratings == [0, 2010, 0, 0, 2010]
    assert len(seen) == 1
    assert seen[0].url.path == "/api/v1/ratings/lookup"
    assert seen[0].headers["x-api-key"] == "the-key"
    assert b"[11,12,13]" in seen[0].content.replace(b" ", b"")


def test_a_refused_batch_falls_back_to_one_by_one(monkeypatch):
    monkeypatch.setattr(
        eloserver,
        "_get_eloserver_asynclient",
        lambda: _client(lambda r: httpx.Response(403)),
    )

    async def one(i):
        return {11: 1800, 12: 1500}.get(i, 0)

    monkeypatch.setattr(eloserver, "get_fideelo", one)

    assert asyncio.run(eloserver.get_fideelos([11, 12, None])) == [1800, 1500, 0]


def test_the_snapshot_fetches_the_ratings_csv_with_the_key(monkeypatch):
    # "Take new snapshot" (interclubs, Reports) answered Internal Server Error:
    # header= instead of headers=, and "//api/..." which httpx reads as a host.
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, text="first_name,last_name,national_id\r\n")

    monkeypatch.setattr(
        eloserver, "_get_eloserver_asynclient", lambda: _client(handler)
    )
    monkeypatch.setattr(eloserver, "get_secret", lambda name: "the-key")

    text = asyncio.run(eloserver.get_ratingcsv())

    assert text.startswith("first_name,")
    assert seen[0].url.path == "/api/v1/players_national/ratings.csv"
    assert seen[0].headers["x-api-key"] == "the-key"


def test_a_refused_snapshot_is_an_error_not_a_file(monkeypatch):
    import pytest
    from fastapi.exceptions import HTTPException

    monkeypatch.setattr(
        eloserver,
        "_get_eloserver_asynclient",
        lambda: _client(lambda r: httpx.Response(403, text="forbidden")),
    )
    monkeypatch.setattr(eloserver, "get_secret", lambda name: "the-key")

    with pytest.raises(HTTPException) as refused:
        asyncio.run(eloserver.get_ratingcsv())
    assert refused.value.status_code == 403


def test_one_rating_goes_to_the_configured_path(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"rating": {"standard": 1999}})

    monkeypatch.setattr(
        eloserver, "_get_eloserver_asynclient", lambda: _client(handler)
    )

    assert asyncio.run(eloserver.get_fideelo(11)) == 1999
    assert seen[0].url.path == "/api/v1/public/rating/11"
