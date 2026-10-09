import hmac

from fastapi.security import APIKeyHeader
from reddevil.core import RdNotAuthorized, get_secret

header_schema = APIKeyHeader(name="X-API-Key")


def validate_header(apikey: str):
    "use reddevil get_secret to get the mail_relay_key and compare it apikey"
    key = get_secret("mailrelay")
    # constant time, so the key cannot be guessed from response times
    if (
        not key
        or not isinstance(apikey, str)
        or not hmac.compare_digest(key.encode(), apikey.encode())
    ):
        raise RdNotAuthorized(description="InvalidKey")
