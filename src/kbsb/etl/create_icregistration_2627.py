import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    get_settings,
    connect_mongodb,
    close_mongodb,
)
from kbsb.interclubs.registrations import create_icregistration, ICRegistration
from dotenv import load_dotenv

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
    async with lifespan(app) as _:
        await create_icregistration(
            ICRegistration(
                name="Woluwe 1200",
                idclub=202,
                teams1=0,
                teams2=0,
                teams3=0,
                teams4=0,
                teams5=1,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
