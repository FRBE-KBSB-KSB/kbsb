# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
from datetime import datetime, timedelta, timezone

from async_lru import alru_cache
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError
from reddevil.core import (
    RdBadRequest,
    RdNotAuthorized,
    get_secret,
    get_setting,
    jwt_encode,
    jwt_getunverifiedpayload,
)

from .md_member import (
    SALT,
    AnonMember,
    LoginValidator,
    Member,
)
from .odoo_member import (
    odoo_anon_getclubmembers,
    odoo_anon_getmember,
    odoo_login,
    odoo_mgmt_getclubmembers,
    odoo_mgmt_getmember,
)

logger = logging.getLogger(__name__)


async def superuser_login(superid: str, password: str) -> str:
    """
    Performs a superuser login with the password stored in GCP secret manager
    returns a JWT token
    """
    token_settings = get_setting("TOKEN")
    try:
        su = get_secret(superid)
        logger.info(f"su {su}")
        if su.get("password") != password:
            raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    except Exception:
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    payload = {
        "sub": superid,
        "exp": datetime.now(tz=timezone.utc)
        + timedelta(minutes=token_settings["timeout"]),
    }
    return jwt_encode(payload, SALT)


async def login(ol: LoginValidator) -> tuple[int, str]:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    if ol.email.startswith("S_"):
        return 0, await superuser_login(ol.email, ol.password)
    return await odoo_login(ol.email, ol.password)


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> str:
    """
    checks a JWT token for validity
    return an str with the if of the member if the token is correctly validated,
    if token is not valid the function :
        - either returns None
        - either raise RdNotAuthorized if raising is set

    """
    token = auth.credentials if auth else None
    if not token:
        raise RdNotAuthorized(description="MissingToken")
    if get_setting("TOKEN").get("nocheck"):
        logger.debug("nocheck return token 0")
        return 0
    logger.info(f"token {token}")
    try:
        payload = jwt_getunverifiedpayload(token)
    except JWTError:
        logger.info("Bad Token 1")
        raise RdNotAuthorized(description="BadToken")
    username = payload.get("sub")
    if not username:
        logger.info("Bad Token 2")
        raise RdNotAuthorized(description="BadToken")
    # try:
    #     jwt_verify(token, get_setting("JWT_SECRET") + SALT)
    # except ExpiredSignatureError as e:
    #     logger.info("Bad Token 3")
    #     logger.debug(f"expired {e}")
    #     raise RdNotAuthorized(description="TokenExpired")
    # except JWTError as e:
    #     logger.info("Bad Token 4")
    #     logger.debug(f"jwt error {e}")
    #     raise RdNotAuthorized(description="BadToken")
    return username


async def mgmt_getmember(idbel: str | int) -> Member:
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    return await odoo_mgmt_getmember(nidbel)


async def mgmt_getclubmembers(idclub: int, active: bool) -> list[Member]:
    """
    find all members of a club
    """
    return await odoo_mgmt_getclubmembers(idclub)


async def anon_getclubmembers(idclub: int) -> list[AnonMember]:
    """
    find all members of a club
    """
    return await odoo_anon_getclubmembers(idclub)


@alru_cache(maxsize=30, ttl=60)
async def anon_getmember(idbel: int) -> AnonMember:
    return await odoo_anon_getmember(idbel)
