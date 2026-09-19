import asyncio
import logging
from contextlib import asynccontextmanager

import aiocsv
import aiofiles
from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    a_close_mongodb,
    a_connect_mongodb,
    get_settings,
    register_app,
)

from kbsb import ROOT_DIR

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
load_dotenv()
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()
logger = logging.getLogger("kbsb")


@asynccontextmanager
async def lifespan(app: FastAPI):
    a_connect_mongodb()
    yield
    await a_close_mongodb()


async def main():
    from kbsb.interclubs.series import script_addteam_icseries

    logger.info("Creating IC series 2627")
    infile = ROOT_DIR / "shared" / "icseries2627.csv"
    async with (
        lifespan(app),
        aiofiles.open(infile, mode="r", encoding="utf-8", newline="") as reader,
    ):
        async for team in aiocsv.AsyncDictReader(reader):
            div = team.get("division", "0")
            division = int(div[0])
            index = div[1:] if len(div) > 1 else ""
            idclub = int(team.get("idclub", "0"))
            pairingnumber = int(team.get("pairingnumber", "0"))
            name = team.get("name", "")
            await script_addteam_icseries(
                division=division,
                name=name,
                idclub=idclub,
                pairingnumber=pairingnumber,
                index=index,
            )
    logger.info("Finished")


if __name__ == "__main__":
    asyncio.run(main())
