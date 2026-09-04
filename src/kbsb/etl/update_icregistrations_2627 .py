import asyncio
import logging
from contextlib import asynccontextmanager
from csv import DictReader

from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    a_close_mongodb,
    a_connect_mongodb,
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
logger = logging.getLogger("kbsb")
logger.info("Started")

ics = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    a_connect_mongodb()
    yield
    await a_close_mongodb()


async def main():
    infile = ROOT_DIR / "shared" / "icseries2627.csv"
    from kbsb.interclubs.registrations import get_icregistrations, update_icregistration

    async with lifespan(app) as _:
        regs = {r.idclub: r for r in await get_icregistrations()}
        with open(infile, "r") as f:
            reader = DictReader(f)
            for row in reader:
                idclub = int(row["ClubId"])
                div = row["Division"].strip()
                divnumber = int(div[0:1])
                mycs = ics.setdefault(idclub, {})
                teamsindiv = mycs.get(f"div{divnumber}", 0)
                teamsindiv += 1
                mycs[f"div{divnumber}"] = teamsindiv
        for idclub, mycs in ics.items():
            updated = False
            reg = regs.get(idclub)
            if not reg:
                logger.warning(f"Club {idclub} not found in registrations")
                continue
            if reg.teams1 != mycs.get("div1", 0):
                reg.teams1 = mycs.get("div1", 0)
                print(f"Update Club {idclub} teams1 to {reg.teams1}")
                updated = True
            if reg.teams2 != mycs.get("div2", 0):
                reg.teams2 = mycs.get("div2", 0)
                print(f"Update Club {idclub} teams2 to {reg.teams2}")
                updated = True
            if reg.teams3 != mycs.get("div3", 0):
                reg.teams3 = mycs.get("div3", 0)
                print(f"Update Club {idclub} teams3 to {reg.teams3}")
                updated = True
            if reg.teams4 != mycs.get("div4", 0):
                reg.teams4 = mycs.get("div4", 0)
                print(f"Update Club {idclub} teams4 to {reg.teams4}")
                updated = True
            if reg.teams5 != mycs.get("div5", 0):
                reg.teams5 = mycs.get("div5", 0)
                print(f"Update Club {idclub} teams5 to {reg.teams5}")
                updated = True
            if reg.teams6 != mycs.get("div6", 0):
                reg.teams6 = mycs.get("div6", 0)
                print(f"Update Club {idclub} teams6 to {reg.teams6}")
                updated = True
            if updated:
                await update_icregistration(
                    reg.id,  # type: ignore
                    reg,
                )


if __name__ == "__main__":
    asyncio.run(main())
