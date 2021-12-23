# copyright Chessdevil Consulting BVBA 2018 - 2020

import os.path
import logging, logging.config

from . import version
from reddevil.common.configreader import SettingsProxy
from fastapi import FastAPI
from fastapi.routing import APIRoute

__all__ = ["app"]

# load settings
settings = SettingsProxy("kbsb.settings")
logging.config.dictConfig(settings.LOG_CONFIG)
backenddir = os.path.dirname(os.path.dirname(__file__))
rootdir = os.path.dirname(backenddir)
log = logging.getLogger("kbsb")
log.info(f"Starting website FRBE-KBSB-KSB v{version} ...")

# load app
app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version=version,
)
url = "/api"

# register the mongob connection
from kbsb.db import get_mongodb
from reddevil.common import register_app

register_app(settings, app, get_mongodb, url)

# import service layer
import kbsb.service

log.info(f"Service layer loaded")

# import api endpoints
import kbsb.api

log.info(f"Api layer loaded")

#    Simplify operation IDs so that generated API clients have simpler function
#    names.

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

# import static html endpoints
import kbsb.static

log.info(f"static html endpoints loaded")
