import logging

log = logging.getLogger(__name__)

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
from reddevil.common import RdException, bearer_schema
from reddevil.service.account import validate_token

from kbsb.main import app
from kbsb.oldkbsb import validate_oldtoken
from .interclub import (
    find_interclubenrollment,
    make_interclubenrollment,
    modify_interclubenrollment,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentUpdate,
)


@app.get("/api/v1/a/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_anon_get_enrollment(idclub: int):
    """
    return an enrollment by idclub
    """
    try:
        return await find_interclubenrollment(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/c/interclub/enrollment", response_model=InterclubEnrollment)
async def api_make_enrollment(
    ie: InterclubEnrollmentIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_oldtoken(auth)
        # TODO check club autorization
        return await make_interclubenrollment(ie)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/c/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_update_enrollment(
    idclub: int,
    iu: InterclubEnrollmentUpdate,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    """
    return an enrollment by idclub
    """
    try:
        return await modify_interclubenrollment(idclub, iu)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")
