import asyncio
import logging
import xmlrpc.client
from datetime import date, datetime
from typing import Any

import httpx
import requests
from fastapi import FastAPI
from reddevil.core import (
    RdBadRequest,
    RdException,
    RdNotFound,
    get_secret,
    get_setting,
)

from kbsb.core.db import get_odoo

from . import AnonMember, Member

logger = logging.getLogger(__name__)

token_settings = get_setting("TOKEN")
odoo_params = get_setting("ODOO_CONNECTION_PARAMETERS")
odoo_secrets = get_secret("odoo")
tzone = get_setting("TZ_BRUSSELS")


def get_extra_asynclient() -> httpx.AsyncClient:
    # we need a separate httpx session so we don't interfere with the cookies
    # in the login session
    # we cache it in the functional attribute session
    if not hasattr(get_extra_asynclient, "session"):
        get_extra_asynclient.session = httpx.AsyncClient(  # type: ignore[attr-defined]
            base_url=odoo_params["url"],
            timeout=httpx.Timeout(odoo_params["timeout"]),
            limits=httpx.Limits(
                max_keepalive_connections=odoo_params["max_keepalive"],
                max_connections=odoo_params["max_connections"],
            ),
        )
    return get_extra_asynclient.session  # type: ignore[attr-defined]


def current_affiliation_year() -> int:
    today = datetime.now(tz=tzone).date()
    year = today.year
    if today.month >= 9:
        year += 1
    return year


_elo_session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30)
_elo_session.mount("https://", _adapter)
_elo_session.mount("http://", _adapter)


def get_fideelo(id: str | int) -> int:
    if not id:
        return 0
    elo_server = get_setting("ELO_SERVER")
    try:
        response = _elo_session.get(f"{elo_server}/{id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                rating = data.get("rating")
                if isinstance(rating, dict):
                    std = rating.get("standard")
                    if isinstance(std, (int, float)):
                        return int(std)
        return 0
    except Exception as e:
        logger.error(f"Error fetching FIDE ELO for id {id}: {e}")
        return 0


async def mgmt_getmember(idmember: int | str) -> Member:
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
        "x_studio_contact_clubid_link",
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
        idclub=member["x_studio_contact_clubid_link"],
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


async def anon_getmember(idmember: int) -> AnonMember:
    member = await mgmt_getmember(idmember)
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


async def anon_getclubmembers(idclub: int) -> list[AnonMember]:
    logger.info(f"get odoo clubmembers for club {idclub}")
    url = odoo_secrets["url"]
    db = odoo_secrets["db"]
    username = odoo_secrets["username"]
    password = odoo_secrets["password"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    domain = [
        ["x_studio_contact_clubid_link", "=", idclub],
        ["x_studio_contact_affiliationyear", "=", current_affiliation_year()],
    ]
    fields = [
        "email_normalized",
        "id",
        "phone_sanitized",
        "x_studio_contact_affiliationyear",
        "x_studio_contact_birthday_date",
        "x_studio_contact_clubid_link",
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
            "limit": 1000,
            "order": "name asc",
        },
    )
    await asyncio.sleep(0)
    if not members:
        return []

    from concurrent.futures import ThreadPoolExecutor

    def fetch_rating(m: dict[str, Any]) -> int:
        return get_fideelo(m.get("x_studio_contact_nationalid_int"))

    with ThreadPoolExecutor(max_workers=20) as executor:
        ratings = list(executor.map(fetch_rating, members))

    return [
        AnonMember(
            birthyear=date.fromisoformat(member["x_studio_contact_birthday_date"]).year
            if member.get("x_studio_contact_birthday_date")
            else 0,
            fiderating=rating,
            fidetitle=member["x_studio_contact_fidetitle"] or "",
            first_name=member["x_studio_contact_firstname"] or "",
            gender=member["x_studio_contact_gender"] or "",
            idclub=member.get("x_studio_contact_clubid_link") or idclub,
            idfide=member.get("x_studio_contact_fideid_int") or 0,
            idnumber=member.get("x_studio_contact_nationalid_int") or 0,
            last_name=member.get("x_studio_contact_name") or "",
            nationalityfide=member["x_studio_contact_fidenat_id"][1][0:3]
            if member.get("x_studio_contact_fidenat_id")
            else "",
            year_affiliation=member.get("x_studio_contact_affiliationyear") or 0,
        )
        for member, rating in zip(members, ratings)  # type: ignore
    ]


async def mgmt_getclubmembers(idclub: int):
    odoo_settings = get_odoo()
    url = odoo_settings["url"]
    db = odoo_settings["db"]
    username = odoo_settings["username"]
    password = odoo_settings["password"]
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    domain = [
        ["x_studio_contact_clubid_link", "=", idclub],
        ["x_studio_contact_affiliationyear", "=", current_affiliation_year()],
    ]
    fields = [
        "email_normalized",
        "id",
        "phone_sanitized",
        "x_studio_contact_affiliationyear",
        "x_studio_contact_birthday_date",
        "x_studio_contact_clubid_link",
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
        Member(  # type: ignore
            birthdate=date.fromisoformat(member["x_studio_contact_birthday_date"]),
            date_affiliation=date(current_affiliation_year(), 1, 1),
            deceased=0,
            email=member["email_normalized"],
            fiderating=get_fideelo(member["x_studio_contact_nationalid_int"]),
            fidetitle=member["x_studio_contact_fidetitle"] or "",
            first_name=member["x_studio_contact_firstname"],
            gender=member["x_studio_contact_gender"],
            idclub=member["x_studio_contact_clubid_link"],
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


async def odoo_email2idbel(email: str, myapp: FastAPI | None = None):

    url = odoo_params.get("url")
    db = odoo_params.get("db")
    password = odoo_secrets.get("password")
    payload = {
        "fields": [
            "id",
            "name",
            "email",
            "x_studio_contact_nationalid_int",
            "x_studio_contact_clubid",
            "x_studio_contact_clubid_link",
        ],
        "domain": [["email", "=", "ruben.decrop@gmail.com"]],
    }
    headers = {
        "X-Odoo-Database": db,
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json",
    }
    client = get_extra_asynclient()
    try:
        response = await client.post(
            url=f"{url}/json/2/res.partner/search_read",
            json=payload,
            headers=headers,
            timeout=5.0,  # 5-second timeout (default is 5.0)
        )
        results = response.json()
        if len(results) != 1:
            logger.info(f"search_read results={results}")
            raise RuntimeError("Odoo search_read failed")
        return results[0]["x_studio_contact_nationalid_int"]
    except httpx.RequestError:
        raise RdException()
