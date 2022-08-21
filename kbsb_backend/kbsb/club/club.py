# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

log = logging.getLogger(__name__)

from typing import cast, Optional, Union

from reddevil.common import (
    encode_model,
    RdNotFound,
)

from . import (
    Club,
    ClubIn,
    ClubList,
    ClubListItem,
    ClubRoleNature,
    DbClub,
)

from kbsb.core import RdForbidden

# basic CRUD actions


async def create_club(c: ClubIn) -> str:
    """
    create a new Club returning its id
    """
    return await DbClub.add(c.dict())


async def delete_club(id: str) -> None:
    """
    delete Club
    """
    await DbClub.delete(id)


async def get_club(id: str, options: dict = {}) -> Club:
    """
    get the club
    """
    _class = options.pop("_class", Club)
    filter = dict(id=id, **options)
    fdict = await DbClub.find_single(filter)
    return encode_model(fdict, _class)


async def get_clubs(options: dict = {}) -> ClubList:
    """
    get all the Clubs
    """
    _class = options.pop("_class", ClubListItem)
    docs = await DbClub.find_multiple(options)
    log.debug(f"docs get_clubs {docs}")
    clubs = [encode_model(d, _class) for d in docs]
    return ClubList(clubs=clubs)


async def update_club(id: str, c: Club, options: dict = {}) -> Club:
    """
    update a club
    """
    log.info(f"id {id} c {c}, dict {c.dict(exclude_unset=True)}")
    validator = options.pop("_class", Club)
    cdict = await DbClub.update(id, c.dict(exclude_unset=True), options)
    log.info(f"updated cdict {cdict}")
    return cast(Club, encode_model(cdict, validator))


async def find_club(idclub: int) -> Optional[Club]:
    """
    find an club by idclub, returns None if not found
    """
    clubs = (await get_clubs({"idclub": idclub})).clubs
    if not clubs:
        return
    return await get_club(clubs[0].id)


async def verify_club_access(
    id_or_idclub: Union[int, str], idnumber: int, role: ClubRoleNature
) -> bool:
    """
    checks if the person identified by idnumber belongs to the memberlist
    of role inside a club, identified by idclub (an int) or id (a str),
    if check fails
    """
    idnumber = int(idnumber)
    log.debug(f"verify {id_or_idclub} {idnumber} {role}")
    if isinstance(id_or_idclub, str):
        try:
            club = await get_club(id_or_idclub)
        except RdNotFound:
            club = None
    else:
        club = await find_club(id_or_idclub)
    log.debug(f"club in verify {club.idclub}")
    if club and club.clubroles:
        for r in club.clubroles:
            log.debug(f"r: {r.nature} {r.memberlist}")
            if role == r.nature:
                if idnumber in r.memberlist:
                    return True
                else:
                    log.debug(f"member not in list {r.nature}")
    raise RdForbidden


def club_locale(club: Club):
    """
    returns the locale of a club, return "nl" if unknown, as this is most common
    """
    if club.federation.startswith("V"):
        return "nl"
    if club.federation.startswith("F"):
        return "fr"
    if club.federation.startswith("D"):
        return "de"
    return "nl"
