import logging
from datetime import date, datetime
from typing import Any

import httpx
from reddevil.core import (  # type: ignore[import-untyped]
    RdBadRequest,
    RdException,
    RdNotFound,
    get_secret,
    get_setting,
)

from kbsb.core.eloserver import get_fideelo

from . import AnonMember, Member

logger = logging.getLogger(__name__)

token_settings = get_setting("TOKEN")
odoo_params = get_setting("ODOO_CONNECTION_PARAMETERS")
odoo_url = odoo_params["url"]
odoo_db = odoo_params["db"]
odoo_timeout = odoo_params["timeout"]
odoo_keepalive = odoo_params["max_keepalive"]
odoo_conns = odoo_params["max_connections"]
odoo_secrets = get_secret("odoo")
odoo_apikey = odoo_secrets["password"]
tzone = get_setting("TZ_BRUSSELS")


def _get_extra_asynclient() -> httpx.AsyncClient:
    # we need a separate httpx session so we don't interfere with the cookies
    # in the login httpx session
    # we make it a singleton by caching it in the functional attribute session
    if not hasattr(_get_extra_asynclient, "session"):
        _get_extra_asynclient.session = httpx.AsyncClient(  # type: ignore[attr-defined]
            base_url=odoo_url,
            timeout=httpx.Timeout(odoo_timeout),
            limits=httpx.Limits(
                max_keepalive_connections=odoo_keepalive,
                max_connections=odoo_conns,
            ),
        )
    return _get_extra_asynclient.session  # type: ignore[attr-defined]


def _current_affiliation_year() -> int:
    today = datetime.now(tz=tzone).date()
    year = today.year
    if today.month >= 9:
        year += 1
    return year


async def mgmt_getmember(idmember: int | str) -> Member:
    """
    use the session linked to the APIkey to get the member from the idbel
    the optional myapp is used when the method is called outside of an http request
    """
    try:
        idmember = int(idmember)
    except ValueError:
        logger.info(f"odoo_mgmt_getmember: invalid idmember {idmember}")
        raise RdBadRequest(description="InvalidMemberID")
    payload = {
        "fields": [
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
        ],
        "domain": [
            ["x_studio_contact_nationalid_int", "=", idmember],
        ],
    }
    headers = {
        "X-Odoo-Database": odoo_db,
        "Authorization": f"Bearer {odoo_apikey}",
        "Content-Type": "application/json",
    }
    client = _get_extra_asynclient()
    try:
        response = await client.post(
            url=f"{odoo_url}/json/2/res.partner/search_read",
            json=payload,
            headers=headers,
            timeout=5.0,  # 5-second timeout (default is 5.0)
        )
        members = response.json()
    except httpx.RequestError:
        raise RdException()
    if not members:
        logger.info(f"odoo_mgmt_getmember: idmember {idmember} not found")
        raise RdNotFound(description="MemberNotFound")
    member: dict[str, Any] = members[0]  # type: ignore
    return Member(
        birthdate=member["x_studio_contact_birthday_date"],
        date_affiliation=date(_current_affiliation_year(), 1, 1),
        deceased=0,
        email=member["email_normalized"] or "",
        fiderating=await get_fideelo(idmember),
        fidetitle=member["x_studio_contact_fidetitle"] or "",
        first_name=member["x_studio_contact_firstname"],
        gender=member["x_studio_contact_gender"],
        idclub=member["x_studio_contact_clubid_link"],
        idfide=member["x_studio_contact_fideid_int"],
        idnumber=idmember,
        last_name=member["x_studio_contact_name"],
        licence_g=False,
        locked=0,
        mobile=member["phone_sanitized"] or "",
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
    """
    get all members currently affiliated to a club represented by idclub
    fetch per member the fiderating
    """
    payload = {
        "domain": [
            ["parent_id.x_studio_contact_clubid", "=", idclub],
            ["x_studio_contact_affiliationyear", "=", _current_affiliation_year()],
        ],
        "fields": [
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
        ],
    }
    headers = {
        "X-Odoo-Database": odoo_db,
        "Authorization": f"Bearer {odoo_apikey}",
        "Content-Type": "application/json",
    }
    client = _get_extra_asynclient()
    try:
        response = await client.post(
            url=f"{odoo_url}/json/2/res.partner/search_read",
            json=payload,
            headers=headers,
            timeout=5.0,  # 5-second timeout (default is 5.0)
        )
        members = response.json()
    except httpx.RequestError:
        raise RdException()
    if not members:
        return []
    # get the ratings of all members
    idbeliter = (m["x_studio_contact_nationalid_int"] for m in members)
    ratings = [await get_fideelo(i) for i in idbeliter]

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
    """
    identical to anon_getclunmbers but for the mgmt
    """
    payload = {
        "domain": [
            ["x_studio_contact_clubid_link", "=", idclub],
            ["x_studio_contact_affiliationyear", "=", _current_affiliation_year()],
        ],
        "fields": [
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
        ],
    }
    headers = {
        "X-Odoo-Database": odoo_db,
        "Authorization": f"Bearer {odoo_apikey}",
        "Content-Type": "application/json",
    }
    client = _get_extra_asynclient()
    try:
        response = await client.post(
            url=f"{odoo_url}/json/2/res.partner/search_read",
            json=payload,
            headers=headers,
            timeout=5.0,
        )
        members = response.json()
    except httpx.RequestError:
        raise RdException()

    if not members:
        return []
    # get the ratings of all members
    idbeliter = (m["x_studio_contact_nationalid_int"] for m in members)
    ratings = [await get_fideelo(i) for i in idbeliter]
    return [
        Member(  # type: ignore
            birthdate=date.fromisoformat(member["x_studio_contact_birthday_date"]),
            date_affiliation=date(_current_affiliation_year(), 1, 1),
            deceased=0,
            email=member["email_normalized"] or "",
            fiderating=rating,
            fidetitle=member["x_studio_contact_fidetitle"] or "",
            first_name=member["x_studio_contact_firstname"],
            gender=member["x_studio_contact_gender"],
            idclub=member["x_studio_contact_clubid_link"],
            idfide=member["x_studio_contact_fideid_int"],
            idnumber=member["x_studio_contact_nationalid_int"],
            last_name=member["x_studio_contact_name"],
            licence_g=False,
            locked=0,
            mobile=member["phone_sanitized"] or "",
            nationalitybel="",
            nationalityfide=member["x_studio_contact_fidenat_id"][1][0:3],
            year_affiliation=member["x_studio_contact_affiliationyear"],
        )
        for member, rating in zip(members, ratings)  # type: ignore
    ]


async def odoo_email2idbel(email: str):
    """
    obtain the idbel from the email using the session linked to the APIkey
    """
    payload = {
        "fields": [
            "name",
            "email_normalized",
            "x_studio_contact_nationalid_int",
        ],
        "domain": [["email", "=", email]],
    }
    headers = {
        "X-Odoo-Database": odoo_db,
        "Authorization": f"Bearer {odoo_apikey}",
        "Content-Type": "application/json",
    }
    client = _get_extra_asynclient()
    try:
        response = await client.post(
            url=f"{odoo_url}/json/2/res.partner/search_read",
            json=payload,
            headers=headers,
            timeout=5.0,
        )
        results = response.json()
        if len(results) != 1:
            logger.info(f"search_read results={results}")
            raise RuntimeError("Odoo search_read failed")
        else:
            member = results[0]
            logger.debug(f"email2idbel: {member}")
            return member["x_studio_contact_nationalid_int"]
    except httpx.RequestError:
        raise RdException()
