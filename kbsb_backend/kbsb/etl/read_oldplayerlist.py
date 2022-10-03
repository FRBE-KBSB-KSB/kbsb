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

from kbsb.interclub import setup_interclubclub, import_oldinterclubplayer
from kbsb.club import get_clubs
from kbsb.oldkbsb import get_interclubplayers, get_activemembers

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


class MongodbInterclubClubWriter:
    async def __aenter__(self):
        return self

    async def write(self, idclub):
        print("setup ", idclub)
        await setup_interclubclub(idclub)

    async def __aexit__(self):
        pass


async def main():
    await connect_mongodb()
    # async with MongodbInterclubClubWriter() as writer:
    #     db = await get_mongodb()
    #     # await db.interclubclub.drop()
    #     clubs = (await get_clubs()).clubs
    #     for c in clubs:
    #         await writer.write(c.idclub)
    pls = get_interclubplayers()
    member_all = get_activemembers().activemembers
    am_cache = {m.idnumber:m for m in member_all}
    for p in pls:
        await import_oldinterclubplayer(p, am_cache)
    await close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())
