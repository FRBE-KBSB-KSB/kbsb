# copyright Ruben Decrop 2012 - 2015

# all database request come in here, but we do not use dataclasess
# if needed we define extra models an do marshalling functions at the service level
# All _id are translatesd to stringified id on output
# All functions expect stringified id as input 

import logging
import asyncio
from datetime import datetime, date, timezone
from typing import Dict, List, Any, Optional 
from reddevil.crud.db_base import DbBase


class DbBook100(DbBase):
    COLLECTION = 'book100'
    DOCUMENTTYPE = 'Book100'
    VERSION = 1
    IDGENERATOR = 'uuid'    
