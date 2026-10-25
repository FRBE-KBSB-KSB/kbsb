# copyright Chessdevil Consulting BVBA 2018 - 2020
# copyright Ruben Decrop 2020 - 2022


import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import RdException, bearer_schema

from kbsb.core import RdForbidden
from kbsb.core.tokens import validate_membertoken, validate_token

from . import (
    AnonMember,
    Login2FAValidator,
    LoginReply,
    LoginValidator,
    Member,
    anon_getclubmembers,
    anon_getmember,
    login,
    login2FA,
    mgmt_getclubmembers,
    mgmt_getmember,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/member")


def get_odoo_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.odoo_client


HttpClient = Annotated[httpx.AsyncClient, Depends(get_odoo_client)]


@router.post("/login", response_model=LoginReply)
async def api_login(
    ol: LoginValidator,
    odoo_client: HttpClient,
) -> LoginReply:
    """
    login by using the idnumber, return a JWT token
    """
    try:
        return await login(ol, odoo_client)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call oldlogin")
        raise HTTPException(status_code=500)


@router.post("/login2FA")
async def api_login2FA(
    l2fa: Login2FAValidator,
    odoo_client: HttpClient,
) -> LoginReply:
    """
    do a 2FA login return a JWT token
    """
    try:
        return await login2FA(l2fa, odoo_client)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call oldlogin")
        raise HTTPException(status_code=500)


@router.get("/anon/clubmembers/{idclub}", response_model=list[AnonMember])
async def api_get_anonclubmembers(idclub: int):
    """
    get all members of a club, returns a list of AnonMember (only name, club and rating)
    """
    try:
        return await anon_getclubmembers(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getclubmembers: {e}")
        raise HTTPException(status_code=500)


@router.get("/mgmt/clubmembers/{idclub}", response_model=list[Member])
async def api_mgmt_clubmembers(
    idclub: int,
    auth: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
):
    """
    get all members of a club, returns a list of AnonMember (only name, club and rating)
    """
    try:
        await validate_token(auth)
        return await mgmt_getclubmembers(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getclubmembers")
        raise HTTPException(status_code=500)


@router.get("/anon/member/{idnumber}", response_model=AnonMember)
async def api_anon_getmember(idnumber: int):
    """
    get a member by his idnumber (only name, club and rating)
    """
    try:
        return await anon_getmember(idnumber)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getmember")
        raise HTTPException(status_code=500)


@router.get("/clb/member/{idmember}", response_model=Member)
async def api_clb_get_member(
    idmember: int,
    auth: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
):
    """
    get full details a member by his idnumber
    """
    try:
        requester = validate_membertoken(auth)
        if requester != str(idmember) and not requester.startswith("SU__"):
            raise RdForbidden
        return await mgmt_getmember(idmember)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call get_activemember")
        raise HTTPException(status_code=500, detail="Internal Server Error")
