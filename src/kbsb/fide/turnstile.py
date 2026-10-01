# Cloudflare Turnstile on the FIDE registration form.
#
# Turnstile is on only when BOTH the site key (TURNSTILE_SITEKEY, public, set
# in app.yaml) and the secret key (Secret Manager "turnstile-secret") are
# there. When either is missing the form works as it always did: no widget,
# no check. So this code can be deployed before the site key is known.
#
# For a manual test on a developer machine (local, prodtest, testing), set
# the environment variables TURNSTILE_SITEKEY and TURNSTILE_SECRET to one of
# Cloudflare's test pairs; Secret Manager is never read in those modes.
#   site keys:   1x00000000000000000000AA (passes), 2x00000000000000000000AB (blocks)
#   secret keys: 1x0000000000000000000000000000000AA (passes),
#                2x0000000000000000000000000000000AA (fails)
#
# The secret is never logged.

import json
import logging
import os
import time

import httpx
from reddevil.core import get_setting

logger = logging.getLogger(__name__)

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
SITEVERIFY_TIMEOUT = 10.0
ACTION = "fide_registration"

# the hostnames the form page is served on; the widget reports the page's own
# hostname, also when the page sits in the blog's iframe
HOSTNAMES = {"www.frbe-kbsb-ksb.be", "frbe-kbsb-ksb.be"}
DEV_HOSTNAMES = {"localhost", "127.0.0.1"}
# Cloudflare's test secret keys answer with action "test"
DEV_ACTIONS = {"test"}

# the modes that run on a developer machine, never on App Engine (as in main.py)
DEV_MODES = ("local", "prodtest", "testing")

# after a failed Secret Manager read, try again after this many seconds
SECRET_RETRY_SECONDS = 300

# message keys in translations.json
MSG_REQUIRED = "turnstile_required"
MSG_FAILED = "turnstile_failed"
MSG_UNAVAILABLE = "turnstile_unavailable"

_secret_cache = {"value": None, "failed_at": 0.0}


def is_dev_mode() -> bool:
    return get_setting("KBSB_MODE") in DEV_MODES


def get_sitekey() -> str:
    return (get_setting("TURNSTILE_SITEKEY") or "").strip()


def _read_secret() -> str:
    if is_dev_mode():
        return os.environ.get("TURNSTILE_SECRET", "").strip()
    sconfig = (get_setting("SECRETS") or {}).get("turnstile")
    if not sconfig:
        return ""
    # Read here, not with reddevil's get_secret: that one only parses JSON or
    # YAML, and the Turnstile secret is stored as the bare key. Same client
    # and project as get_secret.
    from reddevil.core.secrets import secretmanager_client

    project = get_setting("GOOGLE_PROJECT_ID")
    version = sconfig.get("version", "latest")
    reply = secretmanager_client().access_secret_version(
        request={"name": f"projects/{project}/secrets/{sconfig['name']}/versions/{version}"}
    )
    value = reply.payload.data.decode("utf-8").strip()
    if value.startswith("{"):
        value = str(json.loads(value).get("secret", "")).strip()
    return value


def get_secret_key() -> str:
    """The secret key, read once and cached; "" when there is none."""
    if _secret_cache["value"] is not None:
        return _secret_cache["value"]
    failed_at = _secret_cache["failed_at"]
    if failed_at and time.monotonic() - failed_at < SECRET_RETRY_SECONDS:
        return ""
    try:
        value = _read_secret()
    except Exception as e:
        _secret_cache["failed_at"] = time.monotonic()
        logger.warning(f"Turnstile secret could not be read ({type(e).__name__}); Turnstile stays off")
        return ""
    _secret_cache["value"] = value
    return value


def is_enabled() -> bool:
    # the secret is only fetched once a site key is configured
    return bool(get_sitekey()) and bool(get_secret_key())


def sitekey_if_enabled() -> str:
    """The site key for the form page, or "" when Turnstile is off."""
    return get_sitekey() if is_enabled() else ""


def log_status():
    if not get_sitekey():
        logger.info("Turnstile off: no site key configured")
    elif not get_secret_key():
        logger.info("Turnstile off: site key configured but no secret key")
    else:
        logger.info("Turnstile on for the FIDE registration form")


def client_ip(request) -> str:
    ip = request.headers.get("X-Appengine-User-IP", "").strip()
    if ip:
        return ip
    return request.client.host if request.client else ""


async def verify(token: str, remoteip: str) -> str | None:
    """Checks a widget token with Cloudflare.

    Returns None when accepted, else the message key of the refusal. Fails
    closed: when Cloudflare cannot be reached, the submit is refused.
    """
    if not token:
        return MSG_REQUIRED
    data = {"secret": get_secret_key(), "response": token}
    if remoteip:
        data["remoteip"] = remoteip
    try:
        async with httpx.AsyncClient(timeout=SITEVERIFY_TIMEOUT) as client:
            response = await client.post(SITEVERIFY_URL, data=data)
            response.raise_for_status()
            outcome = response.json()
    except Exception as e:
        logger.warning(f"Turnstile siteverify unreachable ({type(e).__name__})")
        return MSG_UNAVAILABLE
    if not isinstance(outcome, dict):
        logger.warning("Turnstile siteverify gave an unreadable answer")
        return MSG_UNAVAILABLE
    hostnames = HOSTNAMES | DEV_HOSTNAMES if is_dev_mode() else HOSTNAMES
    actions = {ACTION} | DEV_ACTIONS if is_dev_mode() else {ACTION}
    hostname = outcome.get("hostname")
    action = outcome.get("action")
    if outcome.get("success") is not True:
        logger.info(f"Turnstile refused: {outcome.get('error-codes')}")
        return MSG_FAILED
    if hostname not in hostnames or action not in actions:
        logger.info(f"Turnstile refused: hostname {hostname!r}, action {action!r}")
        return MSG_FAILED
    return None


async def check(request, token) -> str | None:
    """The check for the submit endpoint: None when Turnstile is off or the
    token is accepted, else the message key of the refusal."""
    from starlette.concurrency import run_in_threadpool

    # the secret is cached after the first read; the first read blocks
    if not await run_in_threadpool(is_enabled):
        return None
    return await verify(str(token or "").strip(), client_ip(request))
