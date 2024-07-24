# copyright Ruben Decrop 2012 - 2024

import logging
from tempfile import NamedTemporaryFile
from typing import cast
import openpyxl
from reddevil.core import (
    RdNotFound,
)
from kbsb.club import get_club_idclub
from kbsb.interclubs import (
    ICVenueDB,
    ICVenueIn,
    DbICVenue,
)

logger = logging.getLogger(__name__)


# CRUD actions


async def create_interclubvenues(iv: ICVenueDB) -> str:
    """
    create a new InterclubVenues returning its id
    """
    ivdict = iv.model_dump()
    ivdict.pop("id", None)
    return await DbICVenue.add(ivdict)


async def get_interclubvenues(id: str, options: dict = {}) -> ICVenueDB:
    """
    get the interclubvenues
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICVenueDB)
    filter["id"] = id
    # return cast(ICVenueDB, await DbICVenue.find_single(filter))
    return await DbICVenue.find_single(filter)


async def get_interclubvenues_clubs(options: dict = {}) -> list[ICVenueDB]:
    """
    get the interclubvenues of all clubs
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICVenueDB)
    return [x for x in await DbICVenue.find_multiple(filter)]


async def update_interclubvenues(
    id: str, iu: ICVenueDB, options: dict = {}
) -> ICVenueDB:
    """
    update a interclub venue
    """
    options1 = options.copy()
    options1["_model"] = options1.get("_model", ICVenueDB)
    iudict = iu.model_dump(exclude_unset=True)
    iudict.pop("id", None)
    return cast(ICVenueDB, await DbICVenue.update(id, iudict, options1))


async def getICvenues(idclub: int) -> ICVenueDB:
    venues = await DbICVenue.find_single({"_model": ICVenueDB, "idclub": idclub})
    return venues


# business logic


async def set_interclubvenues(idclub: str, ivi: ICVenueIn) -> ICVenueDB:
    logger.info(f"running set icvenues {idclub}")
    club = await get_club_idclub(idclub)
    logger.debug(f"set_interclubvenues: {idclub} {ivi}")
    if not club:
        raise RdNotFound(description="ClubNotFound")
    try:
        ivn = await getICvenues(idclub)
        logger.info(f"update interclubvenues {ivn.id}")
        niv = await update_interclubvenues(ivn.id, ivi)
    except RdNotFound:
        iv = ICVenueDB(
            idclub=idclub,
            venues=ivi.venues,
        )
        logger.info(f"insert interclubvenues {iv}")
        id = await create_interclubvenues(iv)
        niv = await get_interclubvenues(id)
    # TODO solve email
    # receiver = (
    #     [club.email_main, settings.INTERCLUB_CC_EMAIL]
    #     if club.email_main
    #     else [settings.INTERCLUB_CC_EMAIL]
    # )
    # if club.email_interclub:
    #     receiver.append(club.email_interclub)
    # mp = MailParams(
    #     locale=locale,
    #     receiver=",".join(receiver),
    #     sender="noreply@frbe-kbsb-ksb.be",
    #     bcc=settings.EMAIL.get("bcc", ""),
    #     subject="Interclub 2022-23",
    #     template="interclub/venues_{locale}.md",
    # )
    # nivdict = niv.dict()
    # nivdict["locale"] = locale
    # nivdict["name"] = club.name_long
    # sendEmail(mp, nivdict, "interclub venues")
    return niv


async def xls_venues() -> str:
    """
    get all venues in csv format
    """
    docs = await get_interclubvenues_clubs()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Venues"
    ws.append(
        [
            "idclub",
            "n.",
            "address",
            "capacity",
            "rounds",
            "teams",
            "wheelchaie",
            "email",
            "phone",
            "remarks",
        ]
    )
    for vns in docs:
        for ix, vn in enumerate(vns.venues):
            logger.info(f"rec {vn} {ix}")
            ws.append(
                [
                    vns.idclub,
                    ix + 1,
                    vn.address,
                    vn.capacity,
                    ",".join(vn.rounds),
                    ",".join(vn.teams),
                    vn.wheelchair,
                    vn.email,
                    vn.phone,
                    vn.remarks,
                ]
            )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        xlscontent = tmp.read()
    return xlscontent
