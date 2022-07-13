import logging

log = logging.getLogger(__name__)

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
from reddevil.common import RdException, bearer_schema
from reddevil.service.account import validate_token

from kbsb.main import app
from kbsb.oldkbsb import validate_oldtoken
from . import (
    find_interclubenrollment,
    find_interclubvenues_club,
    set_interclubenrollment,
    set_interclubvenues,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubVenuesIn,
    InterclubVenues,
)


@app.get("/api/v1/a/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_find_interclubenrollment(idclub: int):
    """
    return an enrollment by idclub
    """
    try:
        return await find_interclubenrollment(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call find_interclubenrollment")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/c/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_set_enrollment(
    idclub: int,
    ie: InterclubEnrollmentIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_oldtoken(auth)
        # TODO check club autorization
        return await set_interclubenrollment(idclub, ie)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/a/interclub/venues/{idclub}", response_model=InterclubVenues)
async def api_find_interclubvenues(idclub: int):
    try:
        return await find_interclubvenues_club(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call find_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/c/interclub/venues/{idclub}", response_model=InterclubVenues)
async def api_set_interclubvenues(
    idclub: int,
    ivi: InterclubVenuesIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_oldtoken(auth)
        # TODO check club autorization
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")
