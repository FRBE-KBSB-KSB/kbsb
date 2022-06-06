# copyright Ruben Decrop 2012 - 2022

import logging, uuid
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
from mimetypes import guess_type
from random import randrange
from base64 import b64encode, b64decode
from typing import cast, Any, IO
from fastapi.responses import Response

from reddevil.common import (
    RdInternalServerError,
    encode_model,
)

from kbsb.models.md_club import (
    Club,
    ClubIn,
    ClubList,
    ClubListItem,
)

from kbsb.db.db_club import DbClub

log = logging.getLogger(__name__)

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
