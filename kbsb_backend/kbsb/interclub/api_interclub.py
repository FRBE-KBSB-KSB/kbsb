import logging

log = logging.getLogger(__name__)

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
from reddevil.common import RdException, bearer_schema
from reddevil.service.account import validate_token

from kbsb.main import app
from kbsb.oldkbsb import validate_oldtoken
from kbsb.interclub import (
    find_interclubenrollment,
    make_enrollment,
    InterclubEnrollment,
    InterclubEnrollmentIn,
)

@app.get("/api/v1/a/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_anon_get_enrollment(
    idclub: int
):
    """
    return an enrollment by idclub
    """
    try:
        await find_interclubenrollment(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/c/interclub/enrollment", response_model=InterclubEnrollment)
async def api_make_enrollment(
    ie: InterclubEnrollmentIn, 
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_oldtoken(auth)
        # TODO check club autorization
        return await make_enrollment(ie)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")
