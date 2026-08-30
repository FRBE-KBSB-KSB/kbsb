# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
from datetime import datetime, timedelta, timezone

from async_lru import alru_cache
from fastapi.security import HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError
from reddevil.core import (
    RdBadRequest,
    RdNotAuthorized,
    get_secret,
    get_setting,
    jwt_encode,
    jwt_getunverifiedpayload,
    jwt_verify,
)

from .md_member import (
    SALT,
    AnonMember,
    LoginValidator,
    Member,
)
from .mysql_member import (
    mysql_anon_getclubmembers,
    mysql_anon_getmember,
    mysql_login,
    mysql_mgmt_getclubmembers,
    mysql_mgmt_getmember,
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


async def login(ol: LoginValidator) -> str:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    dbmember = get_setting("MEMBERDB")
    if ol.idnumber.startswith("S_"):
        return await superuser_login(ol.idnumber, ol.password)
    if dbmember == "oldmysql":
        return await mysql_login(ol.idnumber, ol.password)
    if dbmember == "odoo":
        return await odoo_login(ol.idnumber, ol.password)
    raise NotImplementedError


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> str:
    """
    checks a JWT token for validity
    return an str with the if of the member if the token is correctly validated,
    if token is not valid the function :
        - either returns None
        - either raise RdNotAuthorized if raising is set

    """
    dbmember = get_setting("MEMBERDB")
    token = auth.credentials if auth else None
    if not token:
        raise RdNotAuthorized(description="MissingToken")
    if get_setting("TOKEN").get("nocheck"):
        logger.debug("nocheck return token 0")
        return 0
    try:
        payload = jwt_getunverifiedpayload(token)
    except JWTError:
        raise RdNotAuthorized(description="BadToken")
    username = payload.get("sub")
    try:
        jwt_verify(token, get_setting("JWT_SECRET") + SALT)
    except ExpiredSignatureError as e:
        logger.debug(f"expired {e}")
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError as e:
        logger.debug(f"jwt error {e}")
        raise RdNotAuthorized(description="BadToken")
    return username


async def mgmt_getmember(idbel: str | int) -> Member:
    dbmember = get_setting("MEMBERDB")
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    if dbmember == "oldmysql":
        return await mysql_mgmt_getmember(nidbel)
    elif dbmember == "odoo":
        return await odoo_mgmt_getmember(nidbel)
    raise NotImplementedError


async def mgmt_getclubmembers(idclub: int, active: bool) -> list[Member]:
    """
    find all members of a club
    """
    dbmember = get_setting("MEMBERDB")
    if dbmember == "oldmysql":
        mm = await mysql_mgmt_getclubmembers(idclub, active)
        logger.debug(f"3 mm {mm[0:3]}")
        return mm
    elif dbmember == "odoo":
        return await odoo_mgmt_getclubmembers(idclub, active)
    raise NotImplementedError


async def anon_getclubmembers(idclub: int, active: bool) -> list[AnonMember]:
    """
    find all members of a club
    """
    dbmember = get_setting("MEMBERDB")
    if dbmember == "oldmysql":
        return await mysql_anon_getclubmembers(idclub, active)
    elif dbmember == "odoo":
        return await odoo_anon_getclubmembers(idclub, active)
    raise NotImplementedError


@alru_cache(maxsize=30, ttl=60)
async def anon_getmember(idbel: int) -> AnonMember:
    dbmember = get_setting("MEMBERDB")
    if dbmember == "oldmysql":
        return await mysql_anon_getmember(idbel)
    elif dbmember == "odoo":
        return await odoo_anon_getmember(idbel)
    raise NotImplementedError
