import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from reddevil.common import url, RdException
from reddevil.service.security import bearer_schema, validate_token
from kbsb.service.book100 import (
    createBook100,
    getBooks100,
)
from kbsb.models.md_book100 import Book100In, Book100Optional, Book100List
from kbsb.main import app, url

log = logging.getLogger("kbsb")


@app.post(url + "/book100", response_model=str)
async def api_createBook100(b: Book100In):
    try:
        return await createBook100(b)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call create book100")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get(url + "/book100}", response_model=Book100List)
def api_getBooks100(auth: HTTPAuthorizationCredentials = Depends(bearer_schema)):
    try:
        validate_token(auth)
        return getBooks100()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call getClubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")
