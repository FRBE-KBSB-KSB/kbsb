# copyright Ruben Decrop 2012 - 2026
# copyright Chessdevil Consulting 2015 - 2026

import logging
import logging.config
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from reddevil.core import a_close_mongodb, a_connect_mongodb, get_setting, register_app

from . import version

# the production deployment is the default
# so we should never have code like
# if get_setting("KBSB_MODE") == "production":
#     ...


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The async startup code comes here, it is only called after this file
    is fully loaded, including the settings.
    It is however run before any http request is processed
    """

    # strangely a_connect_mongodb is synchronous, even for the async mongdb driver
    a_connect_mongodb()

    # create an async httpx session to the Odoo platform
    odoo_settings = get_setting("ODOO")
    app.state.odoo_client = httpx.AsyncClient(
        base_url=odoo_settings["url"],
        timeout=httpx.Timeout(odoo_settings["timeout"]),
        limits=httpx.Limits(
            max_keepalive_connections=odoo_settings["max_keepalive"],
            max_connections=odoo_settings["max_connections"],
        ),
    )

    # TODO apply the same for the httpx session to the KBSB database platform

    yield

    # closing down
    await app.state.odoo_client.aclose()
    await a_close_mongodb()


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
logger.info(f"icdata: loading from {get_setting('ICDATA')}")

# add CORS middleware for non production deployments
if get_setting("KBSB_MODE") != "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# import api endpoints
# Ruben Decrop: I removed the existing code bacause it was based
# on tha incorrect assumption that 2 unrelated items: loading
# the endpoints and signing in  with frbe-kbsb-ksb.be accounts,
# are somewhere interfering with each other.  They are not.

logger.info("loading api_account")
from reddevil.account import api_account

logger.info("loading api_club")
from kbsb.club import api_club

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

logger.info("loading api_zerotwocloud_mail")
from zerotwocloud.mail import api as api_zerotwocloud_mail

app.include_router(api_account.router)
app.include_router(api_club.router)
app.include_router(api_interclubs.router)
app.include_router(api_member.router)
app.include_router(api_oldsite.router)
app.include_router(api_fide.router)
app.include_router(api_national_elo_archive.router)
app.include_router(api_players_fide.router)
app.include_router(api_arbiters.router)
app.include_router(api_tournament_registrations.router)
app.include_router(api_zerotwocloud_mail.router)

logger.info("Api's loaded")

# static files
if get_setting("KBSB_MODE") != "production":
    app.mount("/css", StaticFiles(directory="frontend/public/css"), name="css")
    app.mount("/img", StaticFiles(directory="frontend/public/img"), name="img")
    logger.info("static dirs loaded")

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

# test endpoints should always be loaded, even in production
# this is intended behaviour
# this makes the content of test endpoints relevant for security checking
# but currently this is OK
import kbsb.tst_endpoints  # noqa
