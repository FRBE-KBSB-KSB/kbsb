# copyright Ruben Decrop 2015-22

import os.path
import logging, logging.config

from fastapi import FastAPI
from fastapi.routing import APIRoute
from reddevil.common import register_app, get_settings
from kbsb import version


# register app
app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version=version,
)
register_app(app, "kbsb.settings", "/api")
settings = get_settings()
logging.config.dictConfig(settings.LOG_CONFIG)
log = logging.getLogger(__name__)
log.info(f"Starting KBSB ...")

# set up the database async handlers
from reddevil.db import connect_mongodb, close_mongodb
log.info(f"imported connect_mongodb")

app.add_event_handler("startup", connect_mongodb)
app.add_event_handler("shutdown", close_mongodb)
log.info(f"Mongodb event handlers added")

# import service layer
import kbsb.service

log.info(f"Service layer loaded")

# import api endpoints
import kbsb.api

log.info(f"Api layer loaded")

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

# import static endpoints fro rating reports

from kbsb.static import ratingfr, ratingnl

log.info(f"Static path loaded")
