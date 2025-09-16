# reads fide csv file

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
from kbsb.interclubs.series import get_icseries2

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


games = []
players = {}


async def read_icn_round(round: int):
    global games
    series = await get_icseries2()
    for ss in series:
        for r in ss.rounds:
            if r.round != round:
                continue
            for enc in r.encounters:
                for game in enc.games:
                    games.append(game)


async def read_bel_elo():
    global players
    infile = ROOT_DIR / "shared" / "cloud" / "icn" / "bel_elo_202410.csv"
    async with aiofiles.open(infile, mode="r", encoding="utf-8", newline="") as reader:
        async for player in aiocsv.AsyncDictReader(reader):
            players[player["idbel"]] = player


async def main():
    async with lifespan(app) as writer:  # noqa F841
        await read_bel_elo()
        await read_icn_round(1)
        # await update_fide_elo()


if __name__ == "__main__":
    asyncio.run(main())
