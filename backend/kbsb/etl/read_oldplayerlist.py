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
    setup_interclubclub,
    import_oldinterclubplayer,
    clear_interclubclubs,
    sortplayers_interclubclubs,
)
from kbsb.club import get_clubs
from kbsb.oldkbsb import get_oldinterclubplayers, get_activemembers

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
    await clear_interclubclubs()
    print("cleared all interclubplayers")
    pls = get_oldinterclubplayers()
    print("read all old interclubplayers")
    member_all = get_activemembers().activemembers
    print("read all active players")
    am_cache = {m.idnumber: m for m in member_all}
    for ix, p in enumerate(pls):
        await import_oldinterclubplayer(p, am_cache)
        if ix % 100 == 99:
            print(".", end="", flush=True)
    print("added all players to playerlist")
    await sortplayers_interclubclubs()
    print("sorted playerlists")
    await close_mongodb()

#
nonactiveplayers = [12332,8940,36447,15345]


if __name__ == "__main__":
    asyncio.run(main())
