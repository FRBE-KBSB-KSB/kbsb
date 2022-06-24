# copyright Ruben Decrop 2012 - 2022

import logging

log = logging.getLogger(__name__)

from typing import cast, Optional

from reddevil.common import (
    encode_model,
)

from . import (
    Club,
    ClubIn,
    ClubList,
    ClubListItem,
    DbClub,
)


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
    log.info('getting clubs')
    _class = options.pop("_class", ClubListItem)
    docs = await DbClub.find_multiple(options)
    clubs = [encode_model(d, _class) for d in docs]
    return ClubList(clubs=clubs)


async def update_club(id:str, c: Club, options: dict = {}) -> Club:
    """
    update a club
    """
    log.info(f'id {id} c {c}, dict {c.dict(exclude_unset=True)}')
    validator = options.pop("_class", Club)
    cdict = await DbClub.update(id, c.dict(exclude_unset=True), options)
    log.info(f'updated cdict {cdict}')
    return cast(Club, encode_model(cdict, validator))


async def find_club(idclub: str) -> Optional[Club]:
    """
    find an club by idclub, returns None if not found
    """
    clubs = (await get_clubs({'idclub': idclub})).clubs
    if not clubs: 
        return
    return await get_club(clubs[0].id)    


async def verify_club_access(idclub: int, idnumber: int, role: str) -> bool:
    """
    checks if the person identified by idnumber belongs to the memberlist
    of role inside a club, identified by club, 
    returns True if the person has the role, otherwise False
    """
    club = await find_club(idclub)
    log.info(f'club in verify {club}')
    if club and club.clubroles:
        for r in club.clubroles:
            if role == r.nature:
                return idnumber in r.memberlist
    return False
