# copyright Chessdevil Consulting BVBA 2018 - 2020
# copyright Ruben Decrop 2020 - 2022

# this file contains API point that map directly to the old mysql database

import logging

from fastapi import HTTPException
from reddevil.common import RdException
from kbsb.main import app
from kbsb.models.md_old import OldLogin
from kbsb.service.old import do_oldlogin

log = logging.getLogger(__name__)

@app.post("/api/v1/old/login")
def oldlogin(ol: OldLogin) -> str:
    try:
        return do_oldlogin(ol)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call oldlogin")
        raise HTTPException(status_code=500, detail="Internal Server Error")



