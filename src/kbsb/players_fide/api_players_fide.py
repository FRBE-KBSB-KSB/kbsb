import logging
import re

import google.auth
import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/players_fide", tags=["players_fide"])

_api_key_cache = None


def get_api_key() -> str:
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache

    project_id = "website-kbsb-prod"
    try:
        _, p = google.auth.default()
        if p:
            project_id = p
    except Exception:
        pass

    client = secretmanager.SecretManagerServiceClient()
    # players_fide is only reachable with the master-scoped key (see
    # kbsb-dataplatform's apps/dataplatform_api/server.js ROLES) — the
    # oldelo key used by api_national_elo_archive.py is deliberately
    # restricted to national_elo_archive and cannot reach this scope.
    name = f"projects/{project_id}/secrets/hetzner-api-master/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        _api_key_cache = response.payload.data.decode("UTF-8").strip()
        return _api_key_cache
    except Exception:
        logger.exception("Failed to fetch master API key from Secret Manager")
        raise HTTPException(
            status_code=500, detail="Could not retrieve API key for backend"
        )


TARGET_BASE_URL = "https://kbsb-api.zerotwo.cloud/api/v1/players_fide"

# The paths the frontend calls (frontend/api/players_fide.js),
# and nothing else. The proxy adds the master-scoped key, so a free path
# was the whole dataplatform API: "..%2F..%2Fplayers_national/..." left
# this scope, since Starlette decodes %2F and httpx resolves dot segments
# before sending. Segments in the shapes are plain words or digits only.
_ALLOWED_PATHS = [re.compile(p) for p in (r"search", r"[0-9]+")]

# Only these request headers reach the API. Anything else the browser sends,
# above all its own x-* headers, stays here.
_FORWARDED_HEADERS = ("accept", "accept-language", "user-agent")


def _proxied_url(path: str) -> str:
    """
    The upstream URL for `path`, or 404. Segments are plain words only (no
    dots, slashes or percent escapes inside one), the shape must be one the
    frontend uses, and the result must still sit under TARGET_BASE_URL.
    """
    if not any(p.fullmatch(path) for p in _ALLOWED_PATHS):
        raise HTTPException(status_code=404, detail="Not Found")
    url = f"{TARGET_BASE_URL}/{path}"
    if not url.startswith(TARGET_BASE_URL + "/"):
        raise HTTPException(status_code=404, detail="Not Found")
    return url


def _forwarded_headers(request: Request) -> dict:
    return {
        k: v for k, v in request.headers.items() if k.lower() in _FORWARDED_HEADERS
    }

# Read-only lookup (FIDE search + FIDE-ID lookup for tournament organizer
# autofill), so only safe methods are forwarded. Mirrors
# api_national_elo_archive.py's proxy_to_vps almost exactly, just pointed
# at players_fide with the master-scoped key instead of oldelo.
_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client


@router.api_route("/{path:path}", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
async def proxy_to_vps(request: Request, path: str = ""):
    target_url = _proxied_url(path)
    api_key = get_api_key()

    query = request.url.query
    if query:
        target_url = f"{target_url}?{query}"

    headers = _forwarded_headers(request)
    headers["x-api-key"] = api_key
    headers["accept-encoding"] = "identity"

    body = await request.body()
    client = get_client()
    try:
        proxy_response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
        )
    except httpx.RequestError as exc:
        logger.exception(f"An error occurred while requesting {exc.request.url!r}.")
        raise HTTPException(status_code=502, detail="Bad Gateway")

    response_headers = {}
    for k, v in proxy_response.headers.items():
        kl = k.lower()
        if kl not in (
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
            "etag",
            "last-modified",
            "cache-control",
            "set-cookie",
        ) and not kl.startswith("access-control-"):
            response_headers[k] = v
    response_headers["cache-control"] = "no-store"

    return Response(
        content=proxy_response.content,
        status_code=proxy_response.status_code,
        headers=response_headers,
    )
