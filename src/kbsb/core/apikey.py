import hmac

from fastapi.security import APIKeyHeader
from reddevil.core import RdNotAuthorized, get_secret

header_schema = APIKeyHeader(name="X-API-Key")


def validate_header(apikey: str):
    "use reddevil get_secret to get the mail_relay_key and compare it apikey"
    key = get_secret("mailrelay")
    # the "googletext" manager hands back the raw payload, as bytes
    if isinstance(key, bytes):
        key = key.decode()
    key = (key or "").strip()
    # constant time, so the key cannot be guessed from response times
    if (
        not key
        or not isinstance(apikey, str)
        or not hmac.compare_digest(key.encode(), apikey.encode())
    ):
        raise RdNotAuthorized(description="InvalidKey")


def validate_header_incoming(apikey: str, domain: str):
    "validates the incoming api key for the given domain, using the incoming-server secret"
    keys = get_secret("incoming-server")
    if not keys or not isinstance(keys, dict):
        raise RdNotAuthorized(description="InvalidIncomingServerKey")
    key = keys.get(domain, "").strip()
    if (
        not key
        or not isinstance(apikey, str)
        or not hmac.compare_digest(key.encode(), apikey.encode())
    ):
        raise RdNotAuthorized(description="InvalidIncomingServerKey")
