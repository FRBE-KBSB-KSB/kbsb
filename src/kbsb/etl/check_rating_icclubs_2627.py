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

from kbsb.interclubs.icclubs import mgmt_getICclubs
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
            for pl in club.players:
                fiderating = get_fideelo(pl.idnumber) or 0
                if fiderating != pl.fiderating:
                    logger.info(
                        f"Club {club.name} player {pl.first_name} {pl.last_name} ({pl.idnumber}) has rating {pl.fiderating} but FIDE has {fiderating}"
                    )


if __name__ == "__main__":
    asyncio.run(main())
