import asyncio
import logging
from contextlib import asynccontextmanager

import aiocsv
import aiofiles
from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    RdNotFound,
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
    from kbsb.interclubs.md_interclubs import DbICClub, ICClubDB

    logger.info("Updating IC clubs 2627")
    infile = ROOT_DIR / "shared" / "icseries2627.csv"
    async with (
        lifespan(app),
        aiofiles.open(infile, mode="r", encoding="utf-8", newline="") as reader,
    ):
        async for team in aiocsv.AsyncDictReader(reader):
            div = team.get("division", "0")
            index = div[1:] if len(div) > 1 else ""
            idclub = int(team.get("idclub", "0"))
            pairingnr = int(team.get("pairingnumber", "0"))
            name = team.get("name", "")
            if idclub == 0:
                continue
            try:
                club: ICClubDB = await DbICClub.find_single(
                    {"idclub": idclub, "_model": ICClubDB}
                )  # pyright: ignore[reportAssignmentType]
            except RdNotFound:
                logger.exception(f"Error finding club with idclub {idclub}")
                break
            assert club and club.teams
            for t in club.teams:
                if name == t.name:
                    t.pairingnumber = pairingnr
                    t.index = index
            tms = [t.model_dump() for t in club.teams]
            await DbICClub.update({"idclub": idclub}, {"teams": tms})
    logger.info("Finished")


if __name__ == "__main__":
    asyncio.run(main())
