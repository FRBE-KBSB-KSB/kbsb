import asyncio
import pandas as pd
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    get_settings,
    connect_mongodb,
    close_mongodb,
    get_mongodb,
)

from kbsb.interclub import create_oldinterclubmatch
from kbsb.club import get_clubs
from kbsb.oldkbsb import get_oldinterclubgames
from kbsb.oldkbsb.md_oldinterclub import OldInterclubGames

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


class MongodbInterclubMatchWriter:
    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def write(self, oig: OldInterclubGames):
        await create_oldinterclubmatch(oig)

    async def __aexit__(self, *args):
        await close_mongodb()


async def main(round):
    async with MongodbInterclubMatchWriter() as writer:
        for oig in get_oldinterclubgames(round=round).games:
            await writer.write(oig)


if __name__ == "__main__":
    round = 1
    asyncio.run(main(round))
