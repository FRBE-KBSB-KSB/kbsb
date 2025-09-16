import asyncio
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

from kbsb.interclubs.series import get_icseries_all
from kbsb.interclubs.icclubs import mgmt_getICclubs
from kbsb.interclubs.icclubs import DbICClub

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


allseries = {}


async def fill_in_teamsdetails_club():
    clbs = await mgmt_getICclubs()
    for c in clbs:
        for pl in c.players:
            if pl.nature not in ["assigned", "imported"]:
                continue
            if pl.titular:
                for t in c.teams:
                    if t.name == pl.titular and pl.idnumber not in t.titular:
                        t.titular.append(pl.idnumber)
                        break
        for t in c.teams:
            s = allseries.get(t.name)
            if not s:
                print("We are fucked with team", t)
            for st in s.teams:
                if st.name == t.name:
                    t.pairingnumber = st.pairingnumber
                    t.index = st.index
                    break
        await DbICClub.update(
            {"idclub": c.idclub}, {"teams": [t.model_dump() for t in c.teams]}
        )
        # update teams


async def main():
    async with lifespan(app) as writer:  # noqa F841
        for s in await get_icseries_all():
            for st in s.teams:
                if st.idclub:
                    allseries[st.name] = s
        print("allseries keys", "\n".join(allseries.keys()))
        await fill_in_teamsdetails_club()


if __name__ == "__main__":
    asyncio.run(main())
