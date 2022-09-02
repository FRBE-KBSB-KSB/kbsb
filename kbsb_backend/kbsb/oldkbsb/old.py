# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
import hashlib
import asyncio
from jose import JWTError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta, date
from sqlalchemy.orm import sessionmaker
from typing import cast, Any, IO, Union

from reddevil.core import (
    RdNotAuthorized,
    RdNotFound,
    RdBadRequest,
    RdInternalServerError,
    get_settings,
    jwt_encode,
    jwt_getunverifiedpayload,
    jwt_verify,
)
from kbsb.oldkbsb import (
    OldLoginValidator,
    OldMember,
    OldMember_sql,
    OldUser,
    OldUser_sql,
    OldNatRating_sql,
    OldNatRating,
    OldFideRating_sql,
    OldFideRating,
    ActiveMember,
)

from kbsb.core.db import mysql_engine
from .md_old import OldMemberList, OldUser_sql


logger = logging.getLogger(__name__)
# we simplify the normal jwt libs by setting the SALT fixed
SALT = "OLDSITE"


def old_login(ol: OldLoginValidator) -> str:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    query = session.query(OldUser_sql).filter_by(user=ol.idnumber)
    users = query.all()
    if not users:
        logger.info(f"not authorized: idnumber {ol.idnumber} not found")
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
    logger.info(f"not authorized: password hash {pwcheck} not correct")
    raise RdNotAuthorized(description="WrongUsernamePasswordCombination")


def validate_oldtoken(auth: HTTPAuthorizationCredentials) -> int:
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
        logger.info("JWT Token expired")
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError:
        logger.info("Bad JWT Token")
        raise RdNotAuthorized(description="BadToken")
    except:
        logger.exception("General JWT Error")
    logger.debug(f"payload: {payload}")
    return payload.get("sub")


def get_member(idbel: Union[str, int]) -> OldMember:
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    member = session.query(OldMember_sql).filter_by(idnumber=idbel).one_or_none()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    return OldMember.from_orm(member)


def get_clubmembers(idclub: int, active: bool = True) -> OldMemberList:
    """
    find in the signaletique all members of a club
    """
    try:
        settings = get_settings()
        session = sessionmaker(mysql_engine())()
        query = session.query(OldMember_sql).filter_by(idclub=idclub)
        # from septemeber we need to be affilated for the next year
        today = date.today()
        yaff = [today.year + 1]
        if today.month < 9:
            yaff.append(today.year)
        if active:
            query = (
                query.filter(OldMember_sql.year_affiliation.in_(yaff))
                .filter_by(deceased=0)
                .filter_by(locked=0)
            )
        members = [OldMember.from_orm(u) for u in query.all()]
        logger.info(f"found {len(members)} members for club {idclub}")
        return OldMemberList(members=members)
    except Exception:
        logger.exception("it failed")
        raise RdInternalServerError


def get_activemember(idbel: int) -> ActiveMember:
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    member = (
        session.query(OldMember_sql)
        .filter_by(
            idnumber=idbel,
        )
        .one_or_none()
    )
    if not member:
        raise RdNotFound(description="MemberNotFound")
    if member.deceased or member.licence_g or member.year_affiliation != 2023:
        raise RdNotFound(description="MemberNotActive")
    om = OldMember.from_orm(member)
    onr = session.query(OldNatRating_sql).filter_by(idnumber=idbel).one_or_none()
    natrating = 0
    fiderating = 0
    if onr:
        natrating = onr.natrating
        if onr.idfide and onr.idfide > 0:
            ofr = (
                session.query(OldFideRating_sql)
                .filter_by(idfide=onr.idfide)
                .one_or_none()
            )
            if ofr:
                fiderating = ofr.fiderating
    return ActiveMember(
        idnumber=idbel,
        first_name=om.first_name,
        last_name=om.last_name,
        natrating=natrating,
        fiderating=fiderating,
    )
