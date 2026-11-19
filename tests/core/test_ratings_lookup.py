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
