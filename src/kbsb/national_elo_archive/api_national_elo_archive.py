import logging
import re
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
    except Exception:
        logger.exception("Failed to fetch API key from Secret Manager")
        raise HTTPException(status_code=500, detail="Could not retrieve API key for backend")

TARGET_BASE_URL = "https://kbsb-api.zerotwo.cloud/api/v1/national_elo_archive"

# The paths the frontend calls (frontend/api/national_elo_archive.js),
# and nothing else. The proxy adds the oldelo key, so a free path
# was the whole dataplatform API: "..%2F..%2Fplayers_national/..." left
# this scope, since Starlette decodes %2F and httpx resolves dot segments
# before sending. Segments in the shapes are plain words or digits only.
_SEG = r"[A-Za-z0-9_@-]+"
_ALLOWED_PATHS = [
    re.compile(p)
    for p in (
        r"search",
        r"clubs",
        r"clubs/all",
        rf"player/{_SEG}",
        rf"player/{_SEG}/games",
        rf"club/{_SEG}/players",
    )
]

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

# The archive is read-only, so this credential-injecting proxy only forwards
# safe methods. It is public on purpose: it is the archive's only way in for
# browsers, and it attaches the oldelo key for every caller, so anyone can
# read the archive through it. The key only keeps callers from going around
# the website to the VPS directly; it does not limit what they can read here.
@router.api_route("/{path:path}", methods=["GET", "HEAD"])
@router.api_route("", methods=["GET", "HEAD"])
async def proxy_to_vps(request: Request, path: str = ""):
    target_url = _proxied_url(path)
    api_key = get_api_key()

    query = request.url.query
    if query:
        target_url = f"{target_url}?{query}"
    
    # Only a few plain headers are passed on: none of the site's own
    # session or auth state, and none of the browser's x-* headers.
    headers = _forwarded_headers(request)
    headers["x-api-key"] = api_key
    # Every request reaches the VPS from Google's egress IPs, so on its own
    # the API sees one caller for the whole internet. Tell it who the visitor
    # is, so it can rate limit per visitor. X-Appengine-User-IP is set by App
    # Engine itself and cannot be supplied by the browser; this header is set
    # after copying the request headers, so a browser sending its own
    # x-archive-client-ip is overwritten. Local runs fall back to the socket.
    client_ip = request.headers.get("x-appengine-user-ip") or (
        request.client.host if request.client else ""
    )
    headers["x-archive-client-ip"] = client_ip
    # Force uncompressed upstream: httpx cannot decode br/zstd without extra
    # codecs, and we strip Content-Encoding below, so any compressed body would
    # reach the browser as undecodable bytes. Ask the VPS for identity instead.
    headers["accept-encoding"] = "identity"
    # The browser's If-None-Match / If-Modified-Since are not passed on: a 304
    # would make it serve whatever it cached (including a previously poisoned
    # body), so always fetch a full 200 for these dynamic API responses.
    
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
