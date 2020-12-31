# copyright Chessdevil Consulting BVBA 2018 - 2020

import os.path

# load settings
from reddevil.common.configreader import SettingsProxy
settings = SettingsProxy('kbsb.settings')

import logging, logging.config
logging.config.dictConfig(settings.LOG_CONFIG)

version = '1.0.0'
# read VERSION file if it exist in backend or in root directory
backenddir = os.path.dirname(os.path.dirname(__file__))
rootdir = os.path.dirname(backenddir)
try:
    with open(os.path.join(backenddir, 'VERSION')) as fv:
        version = fv.read()
except:
    pass
try:
    with open(os.path.join(rootdir, 'VERSION')) as fv:
        version = fv.read()
except:
    pass     

log = logging.getLogger('kbsb')
log.info(f'Starting website FRBE-KBSB-KSB v{version} ...')

from fastapi import FastAPI
from fastapi.routing import APIRoute

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version=version,
)
url = '/api'

# register the mongob connection
from kbsb.crud import get_mongodb
from reddevil.common import register_app
register_app(settings, app, get_mongodb, url)

# import service layer 
import kbsb.service
log.info(f'Service layer loaded')

# import api endpoints
import kbsb.api
log.info(f'Api layer loaded')

#    Simplify operation IDs so that generated API clients have simpler function
#    names.

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

# import static html endpoints
import kbsb.static
log.info(f'static html endpoints loaded')

