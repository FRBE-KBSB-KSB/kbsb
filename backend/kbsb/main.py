# copyright Ruben Decrop 2015 - 2024
# copyright Chessdevil Consulting 2015 - 2024

import logging, logging.config
import os
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from reddevil.core import register_app, get_settings, connect_mongodb, close_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_mongodb()
    yield
    close_mongodb()


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
settings = get_settings()
logger = logging.getLogger(__name__)
logger.info(f"Starting website KBSB {version}")
logger.info(f"icdata: {settings.ICDATA}")

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


app.include_router(api_account.router)
app.include_router(api_club.router)
app.include_router(api_filestore.router)
app.include_router(api_interclubs.router)
app.include_router(api_member.router)

logger.info("Api's loaded")

# static files
if settings.KBSB_MODE != "production":
    app.mount("/css", StaticFiles(directory="../frontend/public/css"), name="css")
    app.mount("/img", StaticFiles(directory="../frontend/public/img"), name="img")
    logger.info("static dirs loaded")

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

# importing test endpoints
import kbsb.tst_endpoints  # noqa
