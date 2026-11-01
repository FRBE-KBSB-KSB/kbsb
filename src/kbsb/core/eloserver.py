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
        response = await client.get(
            f"/{eloserver_params['path_rating']}/{id}", headers=headers
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


async def get_ratingcsv():
    """
    get a full ratingtable (in csv format)
    possibnle improvement: validate the content of the file
    """
    client = _get_eloserver_asynclient()
    headers = {"x-api-key": get_secret("eloserver")}
    try:
        response = await client.get(
            f"/{eloserver_params['path_ratingcsv']}", header=headers
        )
    except httpx.RequestError:
        logger.exception("Failed calling get_ratingscsv from eloserver")
        raise HTTPException(status_code=502, detail="Bad Gateway")
    except httpx.HTTPStatusError as exc:
        logger.exception("get_ratingcsv failure")
        raise HTTPException(status_code=exc.response.status_code)
    return response.text
