# copyright Ruben Decrop 2012 - 2022

import logging
from typing import cast, Any, Optional, List

from reddevil.common import (
    RdBadRequest,
    RdNotFound,
    encode_model,
)
from reddevil.service.mail import sendEmail, MailParams

from kbsb.interclub.md_interclub import InterclubVenue
from . import (
    DbInterclubEnrollment,
    DbInterclubPrevious,
    DbInterclubVenues,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentUpdate,
    InterclubPrevious,
    InterclubEnrollmentList,
    InterclubVenues,
    InterclubVenueList,
    InterclubVenuesList,
)
from kbsb.club import get_clubs, get_club, club_locale


log = logging.getLogger(__name__)

# basic CRUD actions


async def create_interclubenrollment(c: InterclubEnrollment) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    return await DbInterclubEnrollment.add(c.dict())


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
    id: str, iu: InterclubEnrollmentUpdate, options: dict = {}
) -> InterclubEnrollment:
    """
    update a interclub enrollment
    """
    validator = options.pop("_class", InterclubEnrollment)
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
    return await DbInterclubVenues.add(iv.dict())


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
    id: str, ivl: InterclubVenueList, options: dict = {}
) -> InterclubVenues:
    """
    update a interclub venue
    """
    validator = options.pop("_class", InterclubVenues)
    docdict = await DbInterclubVenues.update(id, ivl.dict(exclude_unset=True), options)
    return cast(InterclubVenues, encode_model(docdict, validator))


# business logic


async def find_interclubenrollment(idclub: str) -> Optional[InterclubEnrollment]:
    """
    find an enrollment by idclub
    """
    enrs = (await get_interclubenrollments({"idclub": idclub})).enrollments
    return enrs[0] if enrs else None


async def make_interclubenrollment(ie: InterclubEnrollmentIn) -> InterclubEnrollment:
    """
    make an new enrollment
    """
    if await find_interclubenrollment(ie.idclub):
        raise RdBadRequest(description="ClubAlreadyEnrolled")
    clubs = (await get_clubs({"idclub": ie.idclub})).clubs
    if clubs:
        club = await get_club(clubs[0].id)
    else:
        raise RdNotFound(description="ClubNotFound")
    log.info(f"club {club}")
    enr_dict = {
        "idclub": ie.idclub,
        "name_long": club.name_long,
        "name_short": club.name_short,
        "locale": club_locale(club),
        "teams1": ie.teams1,
        "teams2": ie.teams2,
        "teams3": ie.teams3,
        "teams4": ie.teams4,
        "teams5": ie.teams5,
    }
    id = await DbInterclubEnrollment.add(enr_dict)
    receiver = club.email_main
    if club.email_interclub:
        receiver = ",".join([club.email_interclub, receiver])
    mp = MailParams(
        locale=enr_dict["locale"],
        receiver=receiver,
        sender="noreply@frbe-kbsb-ksb.be",
        subject="Interclub 2022-23",
        template="interclub/enrollment_{locale}.md",
    )
    sendEmail(mp, enr_dict, "interclub enrollment")
    log.info(f"Enrollment added TODO send confirmation email")
    return await get_interclubenrollment(id)


async def modify_interclubenrollment(
    idclub: str, iu: InterclubEnrollmentUpdate
) -> InterclubEnrollment:
    """
    update a interclub enrollment
    """
    enrs = (await get_interclubenrollments({"idclub": idclub})).enrollments
    if enrs:
        enr = enrs[0]
    else:
        raise RdNotFound(description="EnrollmentNotFound")
    clubs = (await get_clubs({"idclub": idclub})).clubs
    if clubs:
        club = await get_club(clubs[0].id)
    else:
        raise RdNotFound(description="ClubNotFound")
    upd = await update_interclubenrollment(enr.id, iu)
    receiver = club.email_main
    if club.email_interclub:
        receiver = ",".join([club.email_interclub, receiver])
    mp = MailParams(
        locale=club_locale(club),
        receiver=receiver,
        sender="noreply@frbe-kbsb-ksb.be",
        subject="Interclub 2022-23",
        template="interclub/enrollment_{locale}.md",
    )
    enr_dict = upd.dict()
    enr_dict["locale"] = mp.locale
    sendEmail(mp, enr_dict, "interclub enrollment")
    return upd


async def find_interclubvenues_club(idclub: str) -> Optional[InterclubVenues]:
    clvns = (await get_interclubvenues_clubs({"idclub": idclub})).clubvenues
    return clvns[0] if clvns else None


async def set_interclubvenues(idclub: str, ivl: InterclubVenueList) -> InterclubVenues:
    log.debug(f"ivl {ivl}")
    vns = await find_interclubvenues_club(idclub)
    if vns:
        log.debug(f"vns: {vns}")
        return await update_interclubvenues(vns.id, ivl)
    else:
        id = await create_interclubvenues(
            InterclubVenues(idclub=idclub, venues=ivl.venues)
        )
        return await get_interclubvenues(id)
