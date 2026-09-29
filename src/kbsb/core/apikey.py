# copyright Chessdevil Consulting BVBA 2018 - 2024
# copyright Ruben Decrop 2020 - 2024

import hmac

from fastapi.security import APIKeyHeader
from reddevil.core import get_settings, RdNotAuthorized

header_schema = APIKeyHeader(name="X-API-Key")
settings = get_settings()


def validate_header(apikey: str):
    # constant time, so the key cannot be guessed from response times
    if not isinstance(apikey, str) or not hmac.compare_digest(
        settings.API_KEY.encode(), apikey.encode()
    ):
        raise RdNotAuthorized(description="InvalidKey")
