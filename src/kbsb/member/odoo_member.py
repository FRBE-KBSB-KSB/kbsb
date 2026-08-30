import asyncio
import logging
import xmlrpc.client
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests
from reddevil.core import (
    RdBadRequest,
    # RdInternalServerError,
    RdNotAuthorized,
    RdNotFound,
    get_secret,
    get_setting,
    jwt_encode,
)

from kbsb.core.db import get_odoo

from .md_member import SALT, AnonMember, Member

logger = logging.getLogger(__name__)
odoo_settings = get_setting("ODOO")
token_settings = get_setting("TOKEN")
odoo_secrets = get_secret("odoo")


def current_affiliation_year() -> int:
    today = date.today()
    year = today.year
    if today.month >= 9:
        year += 1
    return year


def get_fideelo(id: str | int) -> int:
    elo_server = get_setting("ELO_SERVER")
    try:
        response = requests.get(f"{elo_server}/{id}")
        return response.json()["rating"]["standard"]
    except requests.RequestException as e:
        logger.error(f"Error fetching FIDE ELO for id {id}: {e}")
        return 0


async def odoo_login(idmember: int | str, password: str) -> str:
    if isinstance(idmember, int):
        idmember = str(idmember)
    url = odoo_settings["url"]
    db = odoo_settings["db"]
    logger.info(f"odoo_login: idmember {idmember} url {url} db {db}")
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, idmember, password, {})
    if not uid:
        logger.info(f"user empty: idmember {idmember} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    payload = {
        "sub": idmember,
        "exp": datetime.now(tz=timezone.utc)
        + timedelta(minutes=token_settings["timeout"]),
    }
    await asyncio.sleep(0)
    return jwt_encode(payload, SALT)


async def odoo_mgmt_getmember(idmember: int | str) -> Member:
    try:
        idmember = int(idmember)
    except ValueError:
        logger.info(f"odoo_mgmt_getmember: invalid idmember {idmember}")
        raise RdBadRequest(description="InvalidMemberID")
    url = odoo_secrets["url"]
    db = odoo_secrets["db"]
    username = odoo_secrets["username"]
    password = odoo_secrets["password"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    domain = [
        ["x_studio_contact_nationalid_int", "=", idmember],
    ]
    fields = [
        "email_normalized",
        "id",
        "phone_sanitized",
        "x_studio_contact_affiliationyear",
        "x_studio_contact_birthday_date",
        "x_studio_contact_clubid",
        "x_studio_contact_fideid_int",
        "x_studio_contact_fidenat_id",
        "x_studio_contact_fidetitle",
        "x_studio_contact_firstname",
        "x_studio_contact_gender",
        "x_studio_contact_name",
        "x_studio_contact_nationalid_int",
        "x_studio_contact_nationalfederation",
    ]
    members = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [domain],
        {
            "fields": fields,
            "limit": 100,  # Paginate responses as needed
            "order": "name asc",
        },
    )
    if not members:
        logger.info(f"odoo_mgmt_getmember: idmember {idmember} not found")
        raise RdNotFound(description="MemberNotFound")
    member: dict[str, Any] = members[0]  # type: ignore
    await asyncio.sleep(0)
    return Member(
        birthdate=member["x_studio_contact_birthday_date"],
        date_affiliation=date(current_affiliation_year(), 1, 1),
        deceased=0,
        email=member["email_normalized"],
        fiderating=get_fideelo(idmember),
        fidetitle=member["x_studio_contact_fidetitle"] or "",
        first_name=member["x_studio_contact_firstname"],
        gender=member["x_studio_contact_gender"],
        idclub=member["x_studio_contact_clubid"],
        idfide=member["x_studio_contact_fideid_int"],
        idnumber=idmember,
        last_name=member["x_studio_contact_name"],
        licence_g=False,
        locked=0,
        mobile=member["phone_sanitized"],
        nationalitybel="",
        nationalityfide=member["x_studio_contact_fidenat_id"][1][0:3],
        year_affiliation=member["x_studio_contact_affiliationyear"],
    )


async def odoo_anon_getmember(idmember: int) -> AnonMember:
    member = await odoo_mgmt_getmember(idmember)
    return AnonMember(
        birthyear=member.birthdate.year if member.birthdate else 0,
        fiderating=member.fiderating or 0,
        fidetitle=member.fidetitle or "",
        first_name=member.first_name or "",
        gender=member.gender or "",
        idclub=member.idclub or 0,
        idfide=member.idfide or 0,
        idnumber=member.idnumber or 0,
        last_name=member.last_name or "",
        nationalityfide=member.nationalityfide or "",
        year_affiliation=member.year_affiliation or 0,
    )


async def odoo_anon_getclubmembers(idclub: int):
    odoo_settings = get_odoo()
    url = odoo_settings["url"]
    db = odoo_settings["db"]
    username = odoo_settings["username"]
    password = odoo_settings["password"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    domain = [
        ["x_studio_contact_clubid", "=", idclub],
        ["x_studio_contact_affiliationyear", "=", current_affiliation_year()],
    ]
    fields = [
        "email_normalized",
        "id",
        "phone_sanitized",
        "x_studio_contact_affiliationyear",
        "x_studio_contact_birthday_date",
        "x_studio_contact_clubid",
        "x_studio_contact_fideid_int",
        "x_studio_contact_fidenat_id",
        "x_studio_contact_fidetitle",
        "x_studio_contact_firstname",
        "x_studio_contact_gender",
        "x_studio_contact_name",
        "x_studio_contact_nationalid_int",
        "x_studio_contact_nationalfederation",
    ]
    members = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [domain],
        {
            "fields": fields,
            "order": "name asc",
        },
    )
    await asyncio.sleep(0)

    if not members:
        return []
    return [
        AnonMember(
            birthyear=member["x_studio_contact_birthday_date"].year,
            fiderating=get_fideelo(member["x_studio_contact_nationalid_int"]),
            fidetitle=member["x_studio_contact_fidetitle"] or "",
            first_name=member["x_studio_contact_firstname"],
            gender=member["x_studio_contact_gender"],
            idclub=member["x_studio_contact_clubid"],
            idfide=member["x_studio_contact_fideid_int"],
            idnumber=member["x_studio_contact_nationalid_int"],
            last_name=member["x_studio_contact_name"],
            nationalityfide=member["x_studio_contact_fidenat_id"][1][0:3],
            year_affiliation=member["x_studio_contact_affiliationyear"],
        )
        for member in members  # type: ignore
    ]


async def odoo_mgmt_getclubmembers(idclub: int):
    odoo_settings = get_odoo()
    url = odoo_settings["url"]
    db = odoo_settings["db"]
    username = odoo_settings["username"]
    password = odoo_settings["password"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    domain = [
        ["x_studio_contact_clubid", "=", idclub],
        ["x_studio_contact_affiliationyear", "=", current_affiliation_year()],
    ]
    fields = [
        "email_normalized",
        "id",
        "phone_sanitized",
        "x_studio_contact_affiliationyear",
        "x_studio_contact_birthday_date",
        "x_studio_contact_clubid",
        "x_studio_contact_fideid_int",
        "x_studio_contact_fidenat_id",
        "x_studio_contact_fidetitle",
        "x_studio_contact_firstname",
        "x_studio_contact_gender",
        "x_studio_contact_name",
        "x_studio_contact_nationalid_int",
        "x_studio_contact_nationalfederation",
    ]
    members = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [domain],
        {
            "fields": fields,
            "order": "name asc",
        },
    )
    await asyncio.sleep(0)

    if not members:
        return []
    return [
        Member(
            birthdate=member["x_studio_contact_birthday_date"],
            date_affiliation=date(current_affiliation_year(), 1, 1),
            deceased=0,
            email=member["email_normalized"],
            fiderating=get_fideelo(member["x_studio_contact_nationalid_int"]),
            fidetitle=member["x_studio_contact_fidetitle"] or "",
            first_name=member["x_studio_contact_firstname"],
            gender=member["x_studio_contact_gender"],
            idclub=member["x_studio_contact_clubid"],
            idfide=member["x_studio_contact_fideid_int"],
            idnumber=member["x_studio_contact_nationalid_int"],
            last_name=member["x_studio_contact_name"],
            licence_g=False,
            locked=0,
            mobile=member["phone_sanitized"],
            nationalitybel="",
            nationalityfide=member["x_studio_contact_fidenat_id"][1][0:3],
            year_affiliation=member["x_studio_contact_affiliationyear"],
        )
        for member in members  # type: ignore
    ]
