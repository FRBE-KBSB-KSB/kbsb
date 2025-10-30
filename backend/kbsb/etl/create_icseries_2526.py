import asyncio
import aiofiles
import aiocsv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from reddevil.core import (
    register_app,
    connect_mongodb,
    close_mongodb,
    get_settings,
)
from dotenv import load_dotenv
import logging
from kbsb import ROOT_DIR
from kbsb.interclubs.series import (
    script_addteam_icseries,
    get_icseries2,
    update_icseries,
    ICSeriesUpdate,
)
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
    infile = ROOT_DIR / "shared" / "db" / "icseries2526.csv"
    async with lifespan(app) as _:
        regs = {r.idclub: r for r in await get_icregistrations()}
        for s in await get_icseries2():
            await update_icseries(
                s.division,
                s.index,
                ICSeriesUpdate(teams=[]),
            )
        async with aiofiles.open(
            infile, mode="r", encoding="utf-8", newline=""
        ) as reader:
            async for team in aiocsv.AsyncDictReader(reader):
                idclub = int(team.get("idclub"))
                if idclub > 0:
                    icname = regs[idclub].name
                else:
                    icname = "Bye"
                await script_addteam_icseries(
                    division=int(team.get("division")),
                    index=team.get("index"),
                    name=f"{icname} {team.get('teamnumber')}",
                    pairingnumber=team.get("pairingnr"),
                    idclub=idclub,
                )


if __name__ == "__main__":
    asyncio.run(main())
