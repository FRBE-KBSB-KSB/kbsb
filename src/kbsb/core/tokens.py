import logging
from datetime import UTC, datetime, timedelta

from fastapi.security import HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt
from reddevil.core import RdNotAuthorized, get_secret, get_setting
from reddevil.core.security import get_tokensalt  # type: ignore[import-untyped]

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


def get_member_salt():
    """
    The salt member tokens are signed with. It differs from the salt of admin
    and superuser tokens, so a token handed to a member can never verify as an
    admin token: the two do not share a key.
    """
    return get_salt() + "|member"


def get_2fa_salt():
    return get_salt() + "|2fa"


# how long somebody has to type the 2FA code after the password was accepted
STATE_2FA_MINUTES = 5


def issue_2fa_state(email: str, session_id: str) -> str:
    """
    Signed note, handed to the browser after the password step, saying whose
    Odoo session this is. The 2FA step takes the email from here and never from
    the browser, otherwise anybody with a 2FA account of their own could finish
    their own login and be given the token of somebody else.
    """
    payload = {
        "sub": email,
        "sid": session_id,
        "exp": datetime.now(tz=UTC) + timedelta(minutes=STATE_2FA_MINUTES),
    }
    return jwt.encode(
        payload,
        jwt_settings["secret"] + get_2fa_salt(),
        jwt_settings["algorithm"],
    )


def read_2fa_state(state: str, session_id: str) -> str:
    """
    The email the 2FA state was issued for, provided it was issued for this
    Odoo session and has not expired.
    """
    try:
        claims = jwt.decode(
            state,
            jwt_settings["secret"] + get_2fa_salt(),
            algorithms=[jwt_settings["algorithm"]],
        )
    except ExpiredSignatureError:
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        raise RdNotAuthorized(description="BadToken")
    if not claims.get("sub") or claims.get("sid") != session_id:
        raise RdNotAuthorized(description="BadToken")
    return str(claims["sub"])


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


def _superuser_sub(token: str) -> str:
    """
    Superusers log in with the admin salt but may also use the member routes
    (they are let through to every member's data there), so a token that does
    not verify as a member token is tried as a superuser token. Nobody else
    gets in this way.
    """
    try:
        sub = _claims(token, get_salt()).get("sub")
    except ExpiredSignatureError:
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        logger.info("member token refused: signature does not verify")
        raise RdNotAuthorized(description="BadToken")
    if not sub or not str(sub).startswith("SU__"):
        raise RdNotAuthorized(description="BadToken")
    return str(sub)


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> str:
    token = _token(auth)
    if token_settings.get("nocheck"):
        return "0"
    try:
        sub = _claims(token, get_member_salt()).get("sub")
    except ExpiredSignatureError:
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        return _superuser_sub(token)
    if not sub:
        raise RdNotAuthorized(description="BadToken")
    return str(sub)


async def validate_token(auth: HTTPAuthorizationCredentials) -> str:
    token = _token(auth)
    if token_settings.get("nocheck"):
        return "anonymous"
    sub = _unverified_sub(token)
    # admins are e-mail addresses and superusers SU__ names; a bare number is a
    # member, whatever it was signed with
    if sub.isdigit():
        logger.info("admin token refused: the subject is a member number")
        raise RdNotAuthorized(description="BadToken")

    # reddevil signs an admin's token with the salt of that admin's account,
    # which is how a token stops working when the account is removed; only a
    # superuser (who has no account) is signed with the site's own salt
    salt = get_salt() if sub.startswith("SU__") else await get_tokensalt(sub)
    if not salt:
        logger.info("admin token refused: no account for its subject")
        raise RdNotAuthorized(description="BadToken")
    try:
        claims = _claims(token, salt)
    except ExpiredSignatureError:
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        logger.info("admin token refused: signature does not verify")
        raise RdNotAuthorized(description="BadToken")
    if str(claims.get("sub")) != sub:
        raise RdNotAuthorized(description="BadToken")
    return sub
