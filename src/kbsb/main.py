# copyright Ruben Decrop 2015 - 2024
# copyright Chessdevil Consulting 2015 - 2024

import logging
import logging.config
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from reddevil.core import a_close_mongodb, a_connect_mongodb, get_setting, register_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    a_connect_mongodb()
    yield
    await a_close_mongodb()


from . import version

# register app
app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version=version,
    lifespan=lifespan,
)
load_dotenv()
register_app(app, "kbsb.settings", "/api")
logger = logging.getLogger(__name__)
logger.info(f"Starting website KBSB {version}")
logger.info(f"icdata: {get_setting('ICDATA')}")

# add CORS middleware for dev only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# import api endpoints
logger.info("loading api_account")
from reddevil.account import api_account

logger.info("loading api_club")
from kbsb.club import api_club

logger.info("loading api_filestore")
from reddevil.filestore import api_filestore

logger.info("loading api_interclubs")
from kbsb.interclubs import api_interclubs

logger.info("loading api_member")
from kbsb.member import api_member

logger.info("loading api_oldsite")
from kbsb.oldsite import api_oldsite

logger.info("loading api_fide")
from kbsb.fide import api_fide

logger.info("loading api_national_elo_archive")
from kbsb.national_elo_archive import api_national_elo_archive

logger.info("loading api_players_fide")
from kbsb.players_fide import api_players_fide

logger.info("loading api_arbiters")
from kbsb.arbiters import api_arbiters

logger.info("loading api_tournament_registrations")
from kbsb.tournament_registrations import api_tournament_registrations

app.include_router(api_account.router)
app.include_router(api_club.router)
app.include_router(api_filestore.router)
app.include_router(api_interclubs.router)
app.include_router(api_member.router)
app.include_router(api_oldsite.router)
app.include_router(api_fide.router)
app.include_router(api_national_elo_archive.router)
app.include_router(api_players_fide.router)
app.include_router(api_arbiters.router)
app.include_router(api_tournament_registrations.router)

logger.info("Api's loaded")

# static files
if get_setting("KBSB_MODE") != "production":
    app.mount("/css", StaticFiles(directory="frontend/public/css"), name="css")
    app.mount("/img", StaticFiles(directory="frontend/public/img"), name="img")
    logger.info("static dirs loaded")

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

# importing test endpoints
import kbsb.tst_endpoints  # noqa
