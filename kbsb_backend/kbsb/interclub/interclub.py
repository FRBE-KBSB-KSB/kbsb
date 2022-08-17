# copyright Ruben Decrop 2012 - 2022

import logging
from typing import cast, Any, Optional, List
import io, csv

from reddevil.common import (
    RdBadRequest,
    RdNotFound,
    encode_model,
)
from reddevil.service.mail import sendEmail, MailParams
from reddevil.common import get_settings

from kbsb.interclub.md_interclub import InterclubVenue
from kbsb.club import find_club, club_locale
from . import (
    DbInterclubEnrollment,
    DbInterclubPrevious,
    DbInterclubVenues,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentList,
    InterclubPrevious,
    InterclubVenues,
    InterclubVenuesIn,
    InterclubVenuesList,
)


log = logging.getLogger(__name__)

INTERCLUB_EMAIL = "interclubs@frbe-kbsb-ksb.be"

# basic CRUD actions


async def create_interclubenrollment(enr: InterclubEnrollment) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    enrdict = enr.dict()
    enrdict.pop("id", None)
    return await DbInterclubEnrollment.add(enrdict)


async def get_interclubenrollment(id: str, options: dict = {}) -> InterclubEnrollment:
    """
    get the interclub enrollment
    """
    _class = options.pop("_class", InterclubEnrollment)
    filter = dict(id=id, **options)
    fdict = await DbInterclubEnrollment.find_single(filter)
    return encode_model(fdict, _class)


async def get_interclubenrollments(options: dict = {}) -> InterclubEnrollmentList:
    """
    get the interclub enrollment
    """
    _class = options.pop("_class", InterclubEnrollment)
    docs = await DbInterclubEnrollment.find_multiple(options)
    enrs = [encode_model(d, _class) for d in docs]
    return InterclubEnrollmentList(enrollments=enrs)


async def update_interclubenrollment(
    id: str, iu: InterclubEnrollment, options: dict = {}
) -> InterclubEnrollment:
    """
    update a interclub enrollment
    """
    validator = options.pop("_class", InterclubEnrollment)
    iu.id = None  # don't override the id
    cdict = await DbInterclubEnrollment.update(id, iu.dict(exclude_unset=True), options)
    return cast(InterclubEnrollment, encode_model(cdict, validator))


async def create_interclubprevious(c: InterclubPrevious) -> str:
    """
    create a new InterclubPrevious returning its id
    """
    return await DbInterclubPrevious.add(c.dict())


async def create_interclubvenues(iv: InterclubVenues) -> str:
    """
    create a new InterclubVenues returning its id
    """
    ivdict = iv.dict()
    ivdict.pop("id", None)
    return await DbInterclubVenues.add(ivdict)


async def get_interclubvenues(id: str, options: dict = {}) -> InterclubVenues:
    """
    get the interclubvenues
    """
    _class = options.pop("_class", InterclubVenues)
    filter = dict(id=id, **options)
    fdict = await DbInterclubVenues.find_single(filter)
    return encode_model(fdict, _class)


async def get_interclubvenues_clubs(options: dict = {}) -> InterclubVenuesList:
    """
    get the interclubvenues of all clubs
    """
    _class = options.pop("_class", InterclubVenues)
    docs = await DbInterclubVenues.find_multiple(options)
    log.debug(f"ivsclubs docs: {docs}")
    clubvenues = [encode_model(d, _class) for d in docs]
    return InterclubVenuesList(clubvenues=clubvenues)


async def update_interclubvenues(
    id: str, iu: InterclubVenues, options: dict = {}
) -> InterclubVenues:
    """
    update a interclub venue
    """
    validator = options.pop("_class", InterclubVenues)
    iu.id = None  # don't override the id
    docdict = await DbInterclubVenues.update(id, iu.dict(exclude_unset=True), options)
    return cast(InterclubVenues, encode_model(docdict, validator))


# business logic


async def find_interclubenrollment(idclub: str) -> Optional[InterclubEnrollment]:
    """
    find an enrollment by idclub
    """
    enrs = (await get_interclubenrollments({"idclub": idclub})).enrollments
    return enrs[0] if enrs else None


async def set_interclubenrollment(
    idclub: str, ie: InterclubEnrollmentIn
) -> InterclubEnrollment:
    """
    set enrollment (and overwrite it if it already exists)
    """
    club = await find_club(idclub)
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    settings = get_settings()
    enr = await find_interclubenrollment(idclub)
    if enr:
        nenr = await update_interclubenrollment(
            enr.id,
            InterclubEnrollment(
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            ),
        )
    else:
        id = await create_interclubenrollment(
            InterclubEnrollment(
                idclub=idclub,
                locale=locale,
                name_long=club.name_long,
                name_short=club.name_short,
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            )
        )
        nenr = await get_interclubenrollment(id)
    receiver = [club.email_main, INTERCLUB_EMAIL]
    if club.email_interclub:
        receiver.append(club.email_interclub)
    log.debug(f"EMAIL settings {settings.EMAIL}")
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["bcc"],
        subject="Interclub 2022-23",
        template="interclub/enrollment_{locale}.md",
    )
    sendEmail(mp, nenr.dict(), "interclub enrollment")
    return nenr


async def csv_interclubenrollments() -> str:
    """
    get all enrollments in csv format
    """
    wishes_keys = [
        "wishes.grouping",
        "wishes.split",
        "wishes.regional",
        "wishes.remarks",
    ]
    fieldnames = [
        "idclub",
        "locale",
        "name_long",
        "name_short",
        "teams1",
        "teams2",
        "teams3",
        "teams4",
        "teams5",
        "idinvoice",
        "idpaymentrequest",
    ]
    csvstr = io.StringIO()
    csvf = csv.DictWriter(csvstr, fieldnames + wishes_keys)
    csvf.writeheader()
    for enr in await DbInterclubEnrollment.find_multiple(
        {"_fieldlist": fieldnames + ["wishes"]}
    ):
        id = enr.pop("id", None)
        wishes = enr.pop("wishes", {})
        enr["wishes.grouping"] = wishes.get("grouping", "")
        enr["wishes.split"] = wishes.get("split", "")
        enr["wishes.regional"] = wishes.get("regional", "")
        enr["wishes.remarks"] = wishes.get("remarks", "")
        csvf.writerow(enr)
    return csvstr.getvalue()


async def find_interclubvenues_club(idclub: str) -> Optional[InterclubVenues]:
    clvns = (await get_interclubvenues_clubs({"idclub": idclub})).clubvenues
    return clvns[0] if clvns else None


async def set_interclubvenues(idclub: str, ivi: InterclubVenuesIn) -> InterclubVenues:
    club = await find_club(idclub)
    log.info(f"set_interclubvenues: {idclub} {ivi}")
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    log.info(f"locale {locale}")
    settings = get_settings()
    ivn = await find_interclubvenues_club(idclub)
    iv = InterclubVenues(
        idclub=idclub,
        name_long=club.name_long,
        name_short=club.name_short,
        venues=ivi.venues,
    )
    if ivn:
        log.info(f"update interclubvenues {ivn.id} {iv}")
        niv = await update_interclubvenues(ivn.id, iv)
    else:
        log.info(f"insert interclubvenues {iv}")
        id = await create_interclubvenues(iv)
        niv = await get_interclubvenues(id)
    receiver = [club.email_main, INTERCLUB_EMAIL]
    if club.email_interclub:
        receiver.append(club.email_interclub)
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["bcc"],
        subject="Interclub 2022-23",
        template="interclub/venues_{locale}.md",
    )
    nivdict = niv.dict()
    nivdict["locale"] = locale
    sendEmail(mp, nivdict, "interclub venues")


async def csv_interclubvenues() -> str:
    """
    get all venues in csv format
    """
    fieldnames = [
        "idclub",
        "name_long",
        "name_short",
        "address",
        "email",
        "phone",
        "capacity",
        "notavailable",
    ]
    csvstr = io.StringIO()
    csvf = csv.DictWriter(csvstr, fieldnames)
    csvf.writeheader()
    for vns in await DbInterclubVenues.find_multiple():
        idclub = vns.get("idclub")
        name_long = vns.get("name_long")
        name_short = vns.get("name_short")
        venues = vns.get("venues")
        for v in venues:
            csvf.writerow(
                {
                    "idclub": idclub,
                    "name_long": name_long,
                    "name_short": name_short,
                    "address": v.get("address"),
                    "email": v.get("email"),
                    "phone": v.get("phone"),
                    "capacity": v.get("capacity"),
                    "notavailable": ",".join(v.get("notavailable", [])),
                }
            )
    return csvstr.getvalue()
