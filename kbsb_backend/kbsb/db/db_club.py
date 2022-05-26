# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

# all database request come in here, but we do not use dataclasess
# if needed we define extra models an do marshalling functions at the service level
# All _id are translatesd to stringified id on output
# All functions expect stringified id as input

import logging
import asyncio
from datetime import datetime, date, timezone
from typing import Dict, List, Any, Optional
from reddevil.db.db_base import DbBase


class DbFile(DbBase):
    COLLECTION = "club"
    DOCUMENTTYPE = "Club"
    VERSION = 1
    IDGENERATOR = "objectid"

