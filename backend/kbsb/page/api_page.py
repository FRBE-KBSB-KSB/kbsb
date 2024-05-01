# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2020

import logging
from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import RdException, bearer_schema, validate_token

from . import checkoutpages, checkoutarticles


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/page")


@router.post("/checkout/pages", status_code=201)
async def api_statamic_to_bucket(
    # auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    logger.info('api checkout pages')
    try:
        # await validate_token(auth)
        await checkoutpages()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call statamic_to_bucket")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/checkout/articles", status_code=201)
async def api_statamic_to_bucket(
    # auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    logger.info('api checkout articles')
    try:
        # await validate_token(auth)
        await checkoutarticles()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call statamic_to_bucket")
        raise HTTPException(status_code=500, detail="Internal Server Error")
