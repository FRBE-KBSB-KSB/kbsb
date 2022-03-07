# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

import json
import asyncio
import concurrent.futures
import logging
from pathlib import Path
from fastapi import HTTPException
from kbsb.db import get_mysql

log = logging.getLogger(__name__)


class DbSignaletique:
    @classmethod
    def _getMember(cls, idbel):
        try:
            idbeln = int(idbel)
        except:
            raise HTTPException(status_code=400, detail="CannotConvertIdbelInt")
        with get_mysql().cursor() as c:
            c.execute("select * from signaletique where Matricule = %s", (idbeln,))
            return c.fetchone()

    @classmethod
    async def getMember(cls, idbel: str):
        def fn():
            return cls._getMember(idbel)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fn)
