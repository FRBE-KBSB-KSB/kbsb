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
    make_interclubenrollment,
    modify_interclubenrollment,
    find_interclubvenues_club,
    set_interclubvenues,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentUpdate,
    InterclubVenueList,
    InterclubVenues,
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


@app.get("/api/v1/c/interclub/venues/{idclub}", response_model=InterclubVenues)
async def api_find_interclubvenues(
    idclub: int,
):
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
    ivl: InterclubVenueList,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_oldtoken(auth)
        # TODO check club autorization
        return await set_interclubvenues(idclub, ivl)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")
