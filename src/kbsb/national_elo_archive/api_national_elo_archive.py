import logging
from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import google.auth
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/national_elo_archive", tags=["national_elo_archive"])

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
    # This proxy only ever forwards to /api/v1/national_elo_archive (see
    # TARGET_BASE_URL below) — it genuinely only needs the oldelo-scoped
    # key, never the master one, matching the two-role split in
    # kbsb-dataplatform's dataplatform-api (see that repo's
    # docs/api_key_management.md). Renamed from the old flat single-key
    # secret "KBSB-testing-api" (deleted 2026-07-26) when the API moved to
    # per-role scoped keys.
    name = f"projects/{project_id}/secrets/hetzner-api-oldelo/versions/latest"
    
    try:
        response = client.access_secret_version(request={"name": name})
        _api_key_cache = response.payload.data.decode("UTF-8").strip()
        return _api_key_cache
    except Exception as e:
        logger.exception("Failed to fetch API key from Secret Manager")
        raise HTTPException(status_code=500, detail="Could not retrieve API key for backend")

TARGET_BASE_URL = "https://kbsb-api.zerotwo.cloud/api/v1/national_elo_archive"

# The archive is read-only, so this credential-injecting proxy only forwards
# safe methods. Keep it bound to localhost -- it must never be exposed publicly.
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
    # Don't leak the local site's own session/auth state to the upstream API --
    # this proxy's only job is to attach the archive's service credential.
    headers.pop("cookie", None)
    headers.pop("authorization", None)
    headers["x-api-key"] = api_key
    # Force uncompressed upstream: httpx cannot decode br/zstd without extra
    # codecs, and we strip Content-Encoding below, so any compressed body would
    # reach the browser as undecodable bytes. Ask the VPS for identity instead.
    headers["accept-encoding"] = "identity"
    # Never let the browser revalidate against the upstream ETag: a 304 would
    # make it serve whatever it cached (including a previously poisoned body),
    # so always fetch a full 200 for these dynamic API responses.
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
        # Drop the validators/caching headers too: the browser must not cache
        # these dynamic responses, otherwise a stale (or poisoned) body sticks.
        # Drop set-cookie: this proxy's session is not the upstream API's session,
        # and the browser has no reason to receive cookies scoped to the VPS.
        if kl not in ("content-encoding", "content-length", "transfer-encoding", "connection", "etag", "last-modified", "cache-control", "set-cookie") and not kl.startswith("access-control-"):
            response_headers[k] = v
    response_headers["cache-control"] = "no-store"

    return Response(
        content=proxy_response.content,
        status_code=proxy_response.status_code,
        headers=response_headers
    )
