# copyright Ruben Decrop 2012 - 2022

import logging
from typing import cast, Any, Optional

from reddevil.common import (
    RdBadRequest,
    RdNotFound,
    encode_model,
)
from reddevil.service.mail import sendEmail, MailParams
from . import (
    DbInterclubEnrollment,
    DbInterclubPrevious,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentUpdate,
    InterclubPrevious,
    InterclubEnrollmentList,
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
    return await update_interclubenrollment(enr.id, iu)
