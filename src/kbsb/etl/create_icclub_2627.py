import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    close_mongodb,
    connect_mongodb,
    get_settings,
    register_app,
)

from kbsb.club import Club, get_clubs
from kbsb.interclubs.icclubs import create_icclub
from kbsb.interclubs.md_interclubs import ICClubDB
from kbsb.interclubs.registrations import get_icregistrations

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
load_dotenv()
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()
logger = logging.getLogger("kbsb")
logger.info("Started")


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_mongodb()
    yield
    close_mongodb()


async def main():
    async with lifespan(app) as _:
        clubs = await get_clubs({"_class": Club})
        regs = {r.idclub: r for r in await get_icregistrations()}
        for c in clubs:
            if c.idclub in regs:
                await create_icclub(
                    ICClubDB(
                        name=regs[c.idclub].name,
                        idclub=c.idclub,
                        registered=True,
                    )
                )


if __name__ == "__main__":
    asyncio.run(main())
