# copyright Ruben Decrop 2012 - 2020
import logging
from datetime import datetime, date
from kbsb import settings

log = logging.getLogger('kbsb')

def date2datetime(d: dict, f: str):
    """
    d: document that is used as input to a mongodb operation 
    f: fieldname
    converts field f of the document d from date to datetime
    as mongodb only supports the datetime type
    """
    if f in d and isinstance(d[f], date):
        t = datetime.min.time()
        d[f] = datetime.combine(d[f], t)  

def get_mongodb():
    """
    a singleton function to get the mongodb database asynchronously
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from asyncio import get_event_loop
    if not hasattr(get_mongodb, 'database'):
        loop = get_event_loop()
        client = AsyncIOMotorClient(settings.MONGO_URL, io_loop=loop)
        setattr(get_mongodb, 'database', client[settings.MONGO_DB])
    return get_mongodb.database

# import all database classes

from .db_member import DbMember
from .db_club import DbClub
from .db_book100 import DbBook100