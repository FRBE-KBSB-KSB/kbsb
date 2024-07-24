# copyright Ruben Decrop 2012 - 2024

import logging
from tempfile import NamedTemporaryFile
import openpyxl
from typing import cast, Any
from reddevil.core import (
    RdNotFound,
    get_settings,
)
from reddevil.mail import MailParams
from kbsb.interclubs import (
    ICEnrollment,
    ICEnrollmentIn,
    DbICEnrollment2425,
    # ICDATA,
)
from kbsb.club import get_club_idclub, club_locale
from reddevil.mail import sendEmail

logger = logging.getLogger(__name__)


# CRUD


async def create_icregistration(enr: ICEnrollmentIn) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    enrdict = enr.model_dump()
    enrdict.pop("id", None)
    return await DbICEnrollment2425.add(enrdict)


async def get_icregistration(id: str, options: dict = {}) -> ICEnrollment:
    """
    get the interclub enrollment
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICEnrollment)
    filter["id"] = id
    return cast(ICEnrollment, await DbICEnrollment2425.find_single(filter))


async def get_icregistrations(options: dict = {}) -> list[ICEnrollment]:
    """
    get the interclub enrollment
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICEnrollment)
    return [
        cast(ICEnrollment, x) for x in await DbICEnrollment2425.find_multiple(filter)
    ]


async def update_icregistration(
    id: str, iu: ICEnrollment, options: dict[str, Any] = {}
) -> ICEnrollment:
    """
    update a interclub enrollment
    """
    options1 = options.copy()
    options1["_model"] = options1.pop("_model", ICEnrollment)
    iudict = iu.model_dump(exclude_unset=True)
    iudict.pop("id", None)
    return cast(ICEnrollment, await DbICEnrollment2425.update(id, iudict, options1))


# business methods


async def find_icregistration(idclub: int) -> ICEnrollment | None:
    """
    find an enrollment by idclub
    """
    logger.debug(f"find_interclubenrollment {idclub}")
    enrs = await get_icregistrations({"idclub": idclub})
    return enrs[0] if enrs else None


async def set_icregistration(idclub: int, ie: ICEnrollmentIn) -> ICEnrollment:
    """
    set enrollment (and overwrite it if it already exists)
    """
    club = await get_club_idclub(idclub)
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    settings = get_settings()
    assert settings is not None
    enr = await find_icregistration(idclub)
    if enr:
        assert enr.id
        nenr = await update_icregistration(
            enr.id,
            ICEnrollment(
                name=ie.name,
                locale=locale,
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            ),
        )
    else:
        id = await create_icregistration(
            ICEnrollmentIn(
                idclub=idclub,
                locale=locale,
                name=ie.name,
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            )
        )
        nenr = await get_icregistration(id)
    receiver = (
        [club.email_main, settings.INTERCLUBS_CC_EMAIL]
        if club.email_main
        else [settings.INTERCLUBS_CC_EMAIL]
    )
    if club.email_interclub:
        receiver.append(club.email_interclub)
    logger.debug(f"EMAIL settings {settings.EMAIL}")
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL.get("bcc", ""),
        subject=f"Interclubs 2024-2025 club {idclub} {ie.name}",
        template="interclub/enrollment_{locale}.md",
    )
    sendEmail(mp, nenr.model_dump(), "interclub enrollment")
    return nenr


async def xls_registrations() -> str:
    """
    get all reservations in xls format
    """
    docs = await get_icregistrations()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reservations"
    ws.append(
        [
            "idclub",
            "idinvoice",
            "idpaymentrequest",
            "locale",
            "name",
            "teams1",
            "teams2",
            "teams3",
            "teams4",
            "teams5",
            "grouping",
            "splitting",
            "regional",
            "remarks",
        ]
    )
    for d in docs:
        ws.append(
            [
                d.idclub,
                d.idinvoice,
                d.idpaymentrequest,
                d.locale,
                d.name,
                d.teams1,
                d.teams2,
                d.teams3,
                d.teams4,
                d.teams5,
                d.wishes.get("grouping", ""),
                d.wishes.get("splitting", ""),
                d.wishes.get("regional", ""),
                d.wishes.get("remarks", ""),
            ]
        )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        xlscontent = tmp.read()
    return xlscontent
