# copyright Chessdevil Consulting BVBA 2018 - 2024
# copyright Ruben Decrop 2020 - 2024

import hmac
import logging
import os

from fastapi.security import APIKeyHeader
from reddevil.core import get_settings, RdNotAuthorized

logger = logging.getLogger("kbsb")

header_schema = APIKeyHeader(name="X-API-Key")
settings = get_settings()

# The key of the mail relay lives in Secret Manager ("mail-relay-key"), never
# in the code. On a developer machine (KBSB_MODE local/prodtest/testing) it is
# MAIL_RELAY_KEY in the environment. Read once and kept; fails closed, so a
# key that cannot be read refuses every call instead of letting them in.
_DEV_MODES = ("local", "prodtest", "testing")
_cache = {"key": None}


def _read_key() -> str:
    if settings.KBSB_MODE in _DEV_MODES:
        return os.environ.get("MAIL_RELAY_KEY", "").strip()
    from reddevil.core.secrets import secretmanager_client

    reply = secretmanager_client().access_secret_version(
        request={
            "name": f"projects/{settings.GOOGLE_PROJECT_ID}/secrets/mail-relay-key/versions/latest"
        }
    )
    return reply.payload.data.decode("utf-8").strip()


def relay_key() -> str:
    if _cache["key"] is None:
        try:
            _cache["key"] = _read_key()
        except Exception as e:
            logger.error(f"mail relay key could not be read ({type(e).__name__}); refusing calls")
            return ""
    return _cache["key"]


def validate_header(apikey: str):
    key = relay_key()
    # constant time, so the key cannot be guessed from response times
    if not key or not isinstance(apikey, str) or not hmac.compare_digest(
        key.encode(), apikey.encode()
    ):
        raise RdNotAuthorized(description="InvalidKey")
