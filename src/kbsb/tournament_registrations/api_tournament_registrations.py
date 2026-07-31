import hmac
import logging
import os
from typing import List
from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel
import httpx
import google.auth
from google.cloud import secretmanager

from reddevil.core import get_settings
from reddevil.mail import MailParams
from reddevil.mail.mail import sendEmailMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tournament_registrations", tags=["tournament_registrations"])

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
    # tournament_registrations is only reachable with the master-scoped key
    # (see api_players_fide.py's get_api_key(), which reads the same secret
    # for the same reason) -- the oldelo key used by
    # api_national_elo_archive.py is deliberately restricted to
    # national_elo_archive and cannot reach this scope.
    name = f"projects/{project_id}/secrets/hetzner-api-master/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        _api_key_cache = response.payload.data.decode("UTF-8").strip()
        return _api_key_cache
    except Exception:
        logger.exception("Failed to fetch master API key from Secret Manager")
        raise HTTPException(status_code=500, detail="Could not retrieve API key for backend")

_mail_bridge_secret_cache = None


def get_mail_bridge_secret() -> str:
    # Symmetric secret kbsb-dataplatform's sendEmail() (routes/
    # tournament_registrations.js) presents as X-Mail-Bridge-Secret to prove
    # a POST /send-confirmation call actually came from there, not the open
    # internet -- this endpoint relays through the same live Gmail service
    # account api_fide.py uses for fide_registration, so an unauthenticated
    # version of it would be an open mail relay for anyone who found the URL.
    #
    # TOURNAMENT_REG_MAIL_BRIDGE_SECRET (plain env var) is checked first as a
    # local-dev escape hatch so this endpoint is testable without prod GCP
    # credentials. Production should use the Secret Manager path below
    # (secret name tournament-registrations-mail-bridge, project
    # website-kbsb-prod, mirroring get_api_key() above) -- that secret has
    # NOT been created yet as of this writing; create it (and the matching
    # WEBSITE_MAIL_BRIDGE_SECRET on the VPS side) before relying on this in
    # production. See docs/VPS_tournament_registrations.md §6.
    global _mail_bridge_secret_cache
    if _mail_bridge_secret_cache:
        return _mail_bridge_secret_cache

    env_override = os.environ.get("TOURNAMENT_REG_MAIL_BRIDGE_SECRET")
    if env_override:
        _mail_bridge_secret_cache = env_override
        return _mail_bridge_secret_cache

    try:
        _, project_id = google.auth.default()
    except Exception:
        project_id = "website-kbsb-prod"

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/tournament-registrations-mail-bridge/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        _mail_bridge_secret_cache = response.payload.data.decode("UTF-8").strip()
        return _mail_bridge_secret_cache
    except Exception:
        logger.exception("Failed to fetch mail bridge secret from Secret Manager")
        raise HTTPException(status_code=500, detail="Could not retrieve mail bridge secret")


class SendConfirmationPayload(BaseModel):
    subject: str
    html: str
    bcc: List[str]


# Website-local endpoint -- unlike every other route on this router, this one
# is NOT proxied to the VPS. It exists because kbsb-dataplatform has no
# working SMTP/Gmail setup of its own, while this app already has one
# (reddevil.mail, GMAIL backend, same service account api_fide.py uses for
# fide_registration) -- see docs/VPS_tournament_registrations.md §6. Node
# builds the real email content (buildConfirmationEmail() in routes/
# tournament_registrations.js); this endpoint's only job is to relay a
# pre-built {subject, html, bcc} payload through sendEmailMessage(), gated by
# the shared secret above.
#
# BCC-only, by explicit request -- matches the legacy PHP tool's own
# email_registrations.php exactly: every recipient (arbiters, the registrant,
# organizer, copy addresses) is blind-copied so none of them see each
# other's address. There is deliberately no real "To" recipient here either,
# same as legacy's own zero-AddAddress()-calls PHPMailer send -- see the
# empty receiver="" below (an earlier draft set this to the sender's own
# address, which meant that real inbox got a genuine copy of every
# confirmation email; fixed).
#
# MUST be registered before the catch-all proxy_to_vps routes below: FastAPI/
# Starlette matches routes in registration order, and "/{path:path}" would
# otherwise match "/send-confirmation" first and forward it uselessly to the
# VPS, which has no matching route there. Same ordering issue, same fix, as
# kbsb-dataplatform's own GET /lookup being registered ahead of GET /:id.
@router.post("/send-confirmation")
async def send_confirmation(request: Request, payload: SendConfirmationPayload):
    presented = request.headers.get("x-mail-bridge-secret", "")
    expected = get_mail_bridge_secret()
    if not hmac.compare_digest(presented.encode("utf-8"), expected.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not payload.bcc:
        raise HTTPException(status_code=400, detail="bcc must not be empty")

    settings = get_settings()
    sender_email = settings.EMAIL.get("sender", "noreply@frbe-kbsb-ksb.be")

    # Deliberately empty, not sender_email -- an earlier version set this to
    # the sender's own address to satisfy MailParams.receiver's required-
    # field constraint, but that address is a real inbox (settings.EMAIL
    # ["sender"]) that would then genuinely receive a copy of every
    # confirmation email, unrelated to any of these registrations. An empty
    # string renders as a bare "To:" header (verified: email.message.
    # EmailMessage tolerates this fine) -- no visible recipient at all,
    # matching legacy's own zero-AddAddress()-calls behavior. Real
    # recipients live only in bcc.
    mail_params = MailParams(
        locale="nl",
        receiver="",
        sender=sender_email,
        subject=payload.subject,
        template=payload.html,
        bcc=", ".join(payload.bcc),
    )

    try:
        sendEmailMessage(mail_params)
        logger.info(f"tournament_registrations confirmation email sent, bcc count={len(payload.bcc)}")
    except Exception:
        logger.exception("Failed to send tournament_registrations confirmation email")
        raise HTTPException(status_code=502, detail="Failed to send confirmation email")

    return {"success": True}


TARGET_BASE_URL = "https://kbsb-api.zerotwo.cloud/api/v1/tournament_registrations"

# Unlike api_players_fide.py / api_national_elo_archive.py, this feature has
# real write endpoints (public registration submissions, admin tournament and
# registration CRUD) plus its own admin JWT login, so:
#   - every method is forwarded, not just GET/HEAD
#   - the incoming Authorization header is passed through UNCHANGED instead
#     of being stripped: on the /admin/* routes it carries the arbiter's
#     tournament_registrations JWT (issued by POST /admin/login) through to
#     the upstream Node API, on top of (not instead of) the x-api-key this
#     proxy injects itself below. The public routes ignore Authorization
#     upstream, so forwarding it through unconditionally is safe.
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
@router.api_route("", methods=["GET", "POST", "PUT", "DELETE", "HEAD"])
async def proxy_to_vps(request: Request, path: str = ""):
    api_key = get_api_key()

    target_url = f"{TARGET_BASE_URL}/{path}" if path else TARGET_BASE_URL
    query = request.url.query
    if query:
        target_url = f"{target_url}?{query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("cookie", None)
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
