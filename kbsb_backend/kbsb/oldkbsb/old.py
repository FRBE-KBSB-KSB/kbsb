# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
import hashlib
from jose import JWTError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from typing import cast, Any, IO

from reddevil.common import (
    RdNotAuthorized,
    get_settings,
    jwt_encode,
    jwt_getunverifiedpayload,
    jwt_verify,
)
from kbsb.oldkbsb import (
    OldLogin,
)
from kbsb.oldkbsb import P_User
from kbsb.core.db import mysql_engine

log = logging.getLogger(__name__)

# we simplify the normal jwt libs by setting the SALT fixed
SALT = "OLDSITE"


def do_oldlogin(ol: OldLogin) -> str:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    query = session.query(P_User).filter(P_User.user == ol.idnumber)
    users = query.all()
    if not users:
        log.info(f"not authorized: idnumber {ol.idnumber} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    hash = f"Le guide complet de PHP 5 par Francois-Xavier Bois{ol.password}"
    pwcheck = hashlib.md5(hash.encode("utf-8")).hexdigest()
    for user in users:
        if user.password == pwcheck:
            payload = {
                "sub": str(ol.idnumber),
                "exp": datetime.utcnow() + timedelta(minutes=settings.TOKEN["timeout"]),
            }
            return jwt_encode(payload, SALT)
    log.info(f"not authorized: password hash {pwcheck} not correct")
    raise RdNotAuthorized(description="WrongUsernamePasswordCombination")


async def validate_oldtoken(auth: HTTPAuthorizationCredentials) -> int:
    """
    checks a JWT token for validity
    return an idnumber if the token is correctly validated
    if token is not valid the function :
        - either returns None
        - either raise RdNotAuthorized if raising is set
    """
    settings = get_settings()
    token = auth.credentials if auth else None
    if not token:
        raise RdNotAuthorized(description="MissingToken")
    try:
        payload = jwt_verify(token, settings.JWT_SECRET + SALT)
    except ExpiredSignatureError:
        log.info("JWT Token expired")
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        log.info("Bad JWT Token")
        raise RdNotAuthorized(description="BadToken")
    except:
        log.exception("General JWT Error")
    log.debug(f"payload: {payload}")
    return payload.get("sub")
