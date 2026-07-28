import logging
from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import google.auth
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/players_fide", tags=["players_fide"])

_api_key_cache = None

def get_api_key() -> str:
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache

    try:
        _, project_id = google.auth.default()
    except Exception:
        project_id = "website-kbsb-prod"

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
        raise HTTPException(status_code=500, detail="Could not retrieve API key for backend")

TARGET_BASE_URL = "https://kbsb-api.zerotwo.cloud/api/v1/players_fide"

# Read-only lookup (FIDE search + FIDE-ID lookup for tournament organizer
# autofill), so only safe methods are forwarded. Mirrors
# api_national_elo_archive.py's proxy_to_vps almost exactly, just pointed
# at players_fide with the master-scoped key instead of oldelo.
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

    async with httpx.AsyncClient() as client:
        try:
            proxy_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=30.0
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
