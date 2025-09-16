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
from kbsb.interclubs import DbICSeries

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
fields = [
    "division",
    "index",
    "icclub_home",
    "icclub_visit",
    "idnumber_home",
    "idnumber_visit",
    "result",
    "overruled",
]


@asynccontextmanager
async def lifespan():
    connect_mongodb()
    yield
    close_mongodb()


async def games_round(round):
    games = []
    for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        print(f"processing {series.division} {series.index}")
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        for enc in encounters:
            icclub_home = enc.icclub_home
            icclub_visit = enc.icclub_visit
            if icclub_home == 0 or icclub_visit == 0:
                continue  # skip bye
            for ix, g in enumerate(enc.games):
                games.append(
                    {
                        "division": series.division,
                        "index": series.index,
                        "icclub_home": icclub_home,
                        "icclub_visit": icclub_visit,
                        "idnumber_home": g.idnumber_home,
                        "idnumber_visit": g.idnumber_visit,
                        "result": g.result,
                        "overruled": g.overruled,
                    }
                )
    return games


async def write_csv(games, round):
    infile = ROOT_DIR / "shared" / "cloud" / "icn" / f"results_r{round}.csv"
    async with aiofiles.open(infile, mode="w", encoding="utf-8", newline="") as afp:
        writer = aiocsv.AsyncDictWriter(afp, fields, restval="NULL")
        await writer.writeheader()
        await writer.writerows(games)


async def main():
    round = 1
    async with lifespan() as writer:
        games = await games_round(round)
        await write_csv(games, round)


if __name__ == "__main__":
    asyncio.run(main())
