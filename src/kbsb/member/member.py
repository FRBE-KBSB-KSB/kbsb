# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
from datetime import UTC, datetime, timedelta

from async_lru import alru_cache
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import (
    RdBadRequest,
    RdNotAuthorized,
    get_secret,
    get_setting,
    jwt_encode,
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
    except Exception as e:
        logger.exception(f"Superuser login failed: {e}")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    payload = {
        "sub": superid,
        "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
    }
    return jwt_encode(payload, SALT)


async def login(ol: LoginValidator) -> tuple[int, str]:
    """
    return a JWT token
    """
    if ol.email.startswith("SU__"):
        return 0, await superuser_login(ol.email, ol.password)
    return await odoo_login(ol.email, ol.password)


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> str:
    """
    checks a JWT token for validity
    return an str with the if of the member if the token is correctly validated,
    if token validation fails, the function raises RdNotAuthorized

    """
    from kbsb.core.tokens import validate_membertoken as verified

    return verified(auth)


async def mgmt_getmember(idbel: str | int) -> Member:
    try:
        nidbel = int(idbel)
    except ValueError:
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


@alru_cache(maxsize=150, ttl=60)
async def anon_getmember(idbel: int) -> AnonMember:
    return await odoo_anon_getmember(idbel)
