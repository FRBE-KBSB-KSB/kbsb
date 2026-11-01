import logging

from fastapi.security import HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt
from reddevil.core import RdNotAuthorized, get_secret, get_setting

logger = logging.getLogger(__name__)
jwt_settings = get_setting("JWT")
token_settings = get_setting("TOKEN")


def get_salt():
    """
    singleton returing the salt
    """
    if not hasattr(get_salt, "salt"):
        get_salt.salt = get_secret("salt")["salt"]
    return get_salt.salt


def _claims(token: str, salt: str) -> dict:
    return jwt.decode(
        token,
        jwt_settings["secret"] + salt,
        algorithms=[jwt_settings["algorithm"]],
    )


def _unverified_sub(token: str) -> str:
    try:
        sub = jwt.get_unverified_claims(token).get("sub")
    except JWTError:
        sub = None
    if not sub:
        raise RdNotAuthorized(description="BadToken")
    return str(sub)


def _token(auth: HTTPAuthorizationCredentials | None) -> str:
    token = auth.credentials if auth else None
    if not token:
        raise RdNotAuthorized(description="MissingToken")
    return token


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> str:
    token = _token(auth)
    if token_settings.get("nocheck"):
        return "0"
    try:
        sub = _claims(token, get_salt()).get("sub")
    except ExpiredSignatureError:
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        logger.info("member token refused: signature does not verify")
        raise RdNotAuthorized(description="BadToken")
    if not sub:
        raise RdNotAuthorized(description="BadToken")
    return str(sub)


async def validate_token(auth: HTTPAuthorizationCredentials) -> str:
    token = _token(auth)
    if token_settings.get("nocheck"):
        return "anonymous"
    sub = _unverified_sub(token)

    try:
        claims = _claims(token, get_salt())
    except ExpiredSignatureError:
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        logger.info("admin token refused: signature does not verify")
        raise RdNotAuthorized(description="BadToken")
    if str(claims.get("sub")) != sub:
        raise RdNotAuthorized(description="BadToken")
    return sub
