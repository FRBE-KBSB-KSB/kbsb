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

from kbsb.interclub import (
    DbInterclubSeries,
    InterclubSeries,
    InterclubTeam,
    setup_interclubclub,
)
from kbsb.club import get_clubs

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


class MongodbInterclubGameWriter:
    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def __aexit__(self, *args):
        await close_mongodb()

    async def write(self, idclub):
        print('setup ', idclub)
        await setup_interclubclub(idclub)


async def main():
    async with MongodbInterclubGameWriter() as writer:
        db = await get_mongodb()
        await db.interclubgame.drop()
        series = (await DbInterclubSeries.p_find_multiple()).allseries
        for s in series:
            await writer.write(s)


if __name__ == "__main__":
    asyncio.run(main())
