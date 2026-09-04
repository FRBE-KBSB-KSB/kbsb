import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    a_close_mongodb,
    a_connect_mongodb,
    register_app,
)

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
load_dotenv()
register_app(app=app, settingsmodule="kbsb.settings")
logger = logging.getLogger("kbsb")

from kbsb.interclubs import mgmt_getICclubs
from kbsb.interclubs.icclubs import update_icclub
from kbsb.member.odoo_member import get_fideelo


@asynccontextmanager
async def lifespan(app: FastAPI):
    a_connect_mongodb()
    yield
    await a_close_mongodb()


async def main():
    async with lifespan(app) as _:
        icclubs = await mgmt_getICclubs()
        for club in icclubs:
            assert club
            updating = False
            for pl in club.players:
                fiderating = get_fideelo(pl.idnumber) or 0
                if fiderating != pl.fiderating:
                    pl.fiderating = fiderating
                    updating = True
            if updating:
                await update_icclub(club)
                logger.info(f"Updated {club.name} with new ratings")


if __name__ == "__main__":
    asyncio.run(main())
