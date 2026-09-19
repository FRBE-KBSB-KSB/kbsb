import asyncio
import hashlib
import logging
from datetime import date, datetime, timedelta, timezone
from typing import List

from reddevil.core import (
    RdInternalServerError,
    RdNotAuthorized,
    RdNotFound,
    get_settings,
    jwt_encode,
)

from kbsb.core.db import get_mysql
from kbsb.member.md_member import SALT, AnonMember, Member

logger = logging.getLogger(__name__)


async def mysql_login(idnumber: str, password: str):
    logger.info(f"mysqllogin {idnumber} ")
    settings = get_settings()
    if settings.SHORTCUT_INFOMANIAKLOGIN:  # type: ignore
        # skip login
        payload = {
            "sub": idnumber,
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(minutes=settings.TOKEN["timeout"]),  # type: ignore
        }
        await asyncio.sleep(0)
        return jwt_encode(payload, SALT)
    cnx = get_mysql()
    query = """
        SELECT user, password from p_user WHERE user = %(user)s
    """
    try:
        cursor = cnx.cursor()
        cursor.execute(query, {"user": idnumber})
        user = cursor.fetchone()
    except Exception:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not user:
        logger.info(f"user empty: idnumber {idnumber} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    dbuser, dbpassword = user
    logger.info(f"user found {dbuser}")
    hash = f"Le guide complet de PHP 5 par Francois-Xavier Bois{password}"
    pwcheck = hashlib.md5(hash.encode("utf-8")).hexdigest()
    if dbpassword == pwcheck:
        payload = {
            "sub": idnumber,
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(minutes=settings.TOKEN["timeout"]),  # type: ignore
        }
        await asyncio.sleep(0)
        return jwt_encode(payload, SALT)
    logger.info(f"password hash failed for {idnumber} ")
    raise RdNotAuthorized(description="WrongUsernamePasswordCombination")


def get_elotable() -> str:
    today = date.today()
    elomonth = (today.month - 1) // 3 * 3 + 1
    return f"p_player{today.year}{elomonth:02d}"


def current_affiliation_year() -> int:
    today = date.today()
    year = today.year
    if today.month >= 9:
        year += 1
    return year


async def mysql_mgmt_getmember(idmember: int) -> Member:
    cnx = get_mysql()
    query = """
        SELECT 
            signaletique.Dnaiss as birthdate,
            Decede as deceased, 
            DateAffiliation as date_affiliation,            
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Matricule as idbel,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Nom as last_name,
            signaletique.G as licence_g, 
            signaletique.Locked as locked, 
            signaletique.GSM as mobile, 
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique 
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide ON {elotable}.Fide =  fide.ID_NUMBER 
        WHERE signaletique.Matricule = %(idbel)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable())
        cursor.execute(qf, {"idbel": idmember})
        member = cursor.fetchone()
    except Exception:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    logger.info("member", member)
    await asyncio.sleep(0)
    return Member(**member)


async def mysql_anon_getmember(idnumber: int) -> AnonMember:
    logger.info(f"getbel {idnumber}")
    cnx = get_mysql()
    query = """
        SELECT
            signaletique.Dnaiss as birthdate,
            fide.Elo as fiderating,
            fide.Title as chesstitle,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Matricule as idnumber,
            signaletique.Nom as last_name,
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide on {elotable}.Fide = fide.ID_NUMBER
        WHERE signaletique.Matricule = %(idnumber)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable())
        cursor.execute(qf, {"idnumber": idnumber})
        member = cursor.fetchone()
    except Exception:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    logger.info(f"member {member}")
    await asyncio.sleep(0)
    am = AnonMember(**member)
    am.birthyear = member["birthdate"].year
    return am


async def mysql_mgmt_getclubmembers(idclub: int, active: bool = True) -> List[Member]:
    cnx = get_mysql()
    qactive = " AND signaletique.AnneeAffilie >= %(year)s " if active else ""
    query = """
        SELECT 
            signaletique.Dnaiss as birthdate,
            Decede as deceased, 
            DateAffiliation as date_affiliation,            
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Matricule as idbel,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Nom as last_name,
            signaletique.G as licence_g, 
            signaletique.Locked as locked, 
            signaletique.GSM as mobile, 
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique 
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide ON {elotable}.Fide =  fide.ID_NUMBER
        WHERE signaletique.Club = %(idclub)s {qactive}
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable(), qactive=qactive)
        cursor.execute(
            qf,
            {
                "idclub": idclub,
                "year": current_affiliation_year(),
            },
        )
        members = cursor.fetchall()
    except Exception:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    await asyncio.sleep(0)
    return [Member(**member) for member in members]


async def mysql_anon_getclubmembers(idclub: int, active: bool = True):
    cnx = get_mysql()
    qactive = " AND signaletique.AnneeAffilie >= %(year)s " if active else ""
    query = """
        SELECT 
            signaletique.Dnaiss as birthdate,
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Matricule as idnumber,
            signaletique.Nom as last_name,
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique 
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide ON {elotable}.Fide =  fide.ID_NUMBER
        WHERE signaletique.Club = %(idclub)s {qactive}
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable(), qactive=qactive)
        cursor.execute(
            qf,
            {
                "idclub": idclub,
                "year": current_affiliation_year(),
            },
        )
        members = cursor.fetchall()
    except Exception:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    await asyncio.sleep(0)
    return [AnonMember(**member) for member in members]
