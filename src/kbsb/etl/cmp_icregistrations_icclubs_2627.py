import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    RdNotFound,
    a_close_mongodb,
    a_connect_mongodb,
    register_app,
)

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

    from kbsb.interclubs.icclubs import get_icclub
    from kbsb.interclubs.registrations import get_icregistrations

    async with lifespan(app) as _:
        regs = {r.idclub: r for r in await get_icregistrations()}
        for idclub in regs:
            try:
                icclub = await get_icclub({"idclub": idclub})
            except RdNotFound:
                continue
            t1 = 0
            t2 = 0
            t3 = 0
            t4 = 0
            t5 = 0
            t6 = 0
            for t in icclub.teams:  # type: ignore
                if t.division == 1:
                    t1 += 1
                elif t.division == 2:
                    t2 += 1
                elif t.division == 3:
                    t3 += 1
                elif t.division == 4:
                    t4 += 1
                elif t.division == 5:
                    t5 += 1
                elif t.division == 6:
                    t6 += 1
            if t1 != regs[idclub].teams1:
                print(f"Club {idclub} teams1: {t1} vs {regs[idclub].teams1}")
            if t2 != regs[idclub].teams2:
                print(f"Club {idclub} teams2: {t2} vs {regs[idclub].teams2}")
            if t3 != regs[idclub].teams3:
                print(f"Club {idclub} teams3: {t3} vs {regs[idclub].teams3}")
            if t4 != regs[idclub].teams4:
                print(f"Club {idclub} teams4: {t4} vs {regs[idclub].teams4}")
            if t5 != regs[idclub].teams5:
                print(f"Club {idclub} teams5: {t5} vs {regs[idclub].teams5}")
            if t6 != regs[idclub].teams6:
                print(f"Club {idclub} teams6: {t6} vs {regs[idclub].teams6}")


if __name__ == "__main__":
    asyncio.run(main())
