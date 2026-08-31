import logging
from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import google.auth
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/arbiters", tags=["arbiters"])

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
    # arbiters is reachable with the master-scoped key (see
    # kbsb-dataplatform's apps/dataplatform_api/server.js ROLES)
    name = f"projects/{project_id}/secrets/hetzner-api-master/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        _api_key_cache = response.payload.data.decode("UTF-8").strip()
        return _api_key_cache
    except Exception:
        logger.exception("Failed to fetch master API key from Secret Manager")
        raise HTTPException(status_code=500, detail="Could not retrieve API key for backend")

TARGET_BASE_URL = "https://kbsb-api.zerotwo.cloud/api/v1/arbiters"

# Read-only lookup (FIDE arbiters search + FIDE-ID lookup for tournament arbiter
# autofill), so only safe methods are forwarded. Mirrors
# api_players_fide.py proxy to VPS.
_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

@router.api_route("/{path:path}", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
async def proxy_to_vps(request: Request, path: str = ""):
    api_key = get_api_key()

    target_url = f"{TARGET_BASE_URL}/{path}" if path else TARGET_BASE_URL
    query = request.url.query
    if query:
        target_url = f"{target_url}?{query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("cookie", None)
    headers.pop("authorization", None)
    headers["x-api-key"] = api_key
    headers["accept-encoding"] = "identity"
    headers.pop("if-none-match", None)
    headers.pop("if-modified-since", None)

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
        if kl not in ("content-encoding", "content-length", "transfer-encoding", "connection", "etag", "last-modified", "cache-control", "set-cookie") and not kl.startswith("access-control-"):
            response_headers[k] = v
    response_headers["cache-control"] = "no-store"

    return Response(
        content=proxy_response.content,
        status_code=proxy_response.status_code,
        headers=response_headers
    )
