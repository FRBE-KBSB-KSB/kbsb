import logging

import httpx
from fastapi.exceptions import HTTPException
from reddevil.core import get_secret, get_setting  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# We create an isolated httpx session to connect to the Eloserver database platform
# An isolated session guarantees we don't interfere with the cookies
# in the login httpx session

eloserver_params = get_setting("ELOSERVER_CONNECTION_PARAMETERS")
eloserver_url = eloserver_params["url"]
eloserver_secret = get_secret("eloserver")


def _get_eloserver_asynclient() -> httpx.AsyncClient:
    # we make it a singleton by caching it in the functional attribute session
    if not hasattr(_get_eloserver_asynclient, "session"):
        _get_eloserver_asynclient.session = httpx.AsyncClient(  # type: ignore[attr-defined]
            base_url=eloserver_url,
            timeout=httpx.Timeout(eloserver_params["timeout"]),
            limits=httpx.Limits(
                max_keepalive_connections=eloserver_params["max_keepalive"],
                max_connections=eloserver_params["max_connections"],
            ),
        )
    return _get_eloserver_asynclient.session  # type: ignore[attr-defined]


async def get_fideelo(id: str | int) -> int:
    """
    get the fiderating for an idbel
    """
    if not id:
        return 0
    client = _get_eloserver_asynclient()
    headers = {"x-api-key": eloserver_secret}
    try:
        # path_rating already starts with "/"; a second one ("//api/...")
        # makes httpx read "api" as a host and drop it from the path.
        response = await client.get(
            f"{eloserver_params['path_rating']}/{id}", headers=headers
        )
    except httpx.RequestError:
        logger.exception("Failed to get_fideelo from eloserver")
        raise HTTPException(status_code=502, detail="Bad Gateway")
    except httpx.HTTPStatusError as exc:
        logger.exception("get_fideelo failure")
        raise HTTPException(status_code=exc.response.status_code)
    try:
        data = response.json()
    except Exception:  # noqa
        return 0
    if isinstance(data, dict):
        rating = data.get("rating")
        if isinstance(rating, dict):
            std = rating.get("standard")
            if isinstance(std, (int, float)):
                return int(std)
    return 0


# the API takes at most this many ids per request
RATINGS_LOOKUP_MAX = 1000


async def get_fideelos(ids) -> list[int]:
    """
    The standard ratings of many members, in the order of ids (0 = unrated or
    unknown). One keyed request per 1000 members instead of one public request
    per member: the public route allows 300 requests a minute, and every
    request from this site comes from the same Google address, so two big
    club pages in a minute would run out. If the API refuses the batch (an
    older API, or a key without the ratings scope), the ratings are fetched one
    by one as before, so a club page never loses its ratings over this.
    """
    ids = list(ids)
    wanted = sorted({int(i) for i in ids if i and int(i) > 0})
    found: dict[int, int] = {}
    try:
        for start in range(0, len(wanted), RATINGS_LOOKUP_MAX):
            chunk = wanted[start : start + RATINGS_LOOKUP_MAX]
            response = await _get_eloserver_asynclient().post(
                eloserver_params["path_ratings_lookup"],
                json={"national_ids": chunk},
                headers={"x-api-key": eloserver_secret},
            )
            response.raise_for_status()
            for key, rating in (response.json().get("ratings") or {}).items():
                std = rating.get("standard") if isinstance(rating, dict) else None
                if isinstance(std, (int, float)):
                    found[int(key)] = int(std)
    except Exception as e:  # noqa: BLE001
        logger.warning(
            f"ratings lookup refused ({type(e).__name__}), one by one instead"
        )
        return [await get_fideelo(i) for i in ids]
    return [found.get(int(i), 0) if i else 0 for i in ids]


async def get_ratingcsv():
    """
    get a full ratingtable (in csv format)
    possibnle improvement: validate the content of the file
    """
    client = _get_eloserver_asynclient()
    headers = {"x-api-key": get_secret("eloserver")}
    try:
        # headers=, not header= (a TypeError, so "Take new snapshot" answered
        # Internal Server Error); the path as configured, it starts with "/";
        # and a refusal raised, so an error page is never stored as a snapshot.
        response = await client.get(eloserver_params["path_ratingcsv"], headers=headers)
        response.raise_for_status()
    except httpx.RequestError:
        logger.exception("Failed calling get_ratingscsv from eloserver")
        raise HTTPException(status_code=502, detail="Bad Gateway")
    except httpx.HTTPStatusError as exc:
        logger.exception("get_ratingcsv failure")
        raise HTTPException(status_code=exc.response.status_code)
    return response.text
