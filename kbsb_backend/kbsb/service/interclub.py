# copyright Ruben Decrop 2012 - 2022

import logging, uuid
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
from random import randrange
from typing import cast, Any, IO
from fastapi.responses import Response

from reddevil.common import (
    RdInternalServerError,
    encode_model,
)

from kbsb.models.md_interclub import (
    InterclubEnrollment,
    InterclubPrevious,
)

from kbsb.db.db_interclub import DbInterclubEnrollment, DbInterclubPrevious

log = logging.getLogger(__name__)

# basic CRUD actions

async def create_interclubenrollment(c: InterclubEnrollment) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    return await DbInterclubEnrollment.add(c.dict())


# async def delete_interclubenrollment(id: str) -> None:
#     """
#     delete InterclubEnrollment
#     """
#     await DbInterclubEnrollment.delete(id)


# async def get_interclubenrollment(id: str, options: dict = {}) -> InterclubEnrollment:
#     """
#     get the club
#     """
#     _class = options.pop("_class", InterclubEnrollment)
#     filter = dict(id=id, **options)
#     fdict = await DbInterclubEnrollment.find_single(filter)
#     return encode_model(fdict, _class)


# async def get_interclubenrollments(options: dict = {}) -> InterclubEnrollmentList:
#     """
#     get all the InterclubEnrollments
#     """
#     log.info('getting clubs')
#     _class = options.pop("_class", InterclubEnrollmentListItem)
#     docs = await DbInterclubEnrollment.find_multiple(options)
#     clubs = [encode_model(d, _class) for d in docs]
#     return InterclubEnrollmentList(clubs=clubs)



# async def update_interclubenrollment(id:str, c: InterclubEnrollment, options: dict = {}) -> InterclubEnrollment:
#     """
#     update a club
#     """
#     log.info(f'id {id} c {c}, dict {c.dict(exclude_unset=True)}')
#     validator = options.pop("_class", InterclubEnrollment)
#     cdict = await DbInterclubEnrollment.update(id, c.dict(exclude_unset=True), options)
#     log.info(f'updated cdict {cdict}')
#     return cast(InterclubEnrollment, encode_model(cdict, validator))

async def create_interclubprevious(c: InterclubPrevious) -> str:
    """
    create a new InterclubPrevious returning its id
    """
    return await DbInterclubPrevious.add(c.dict())