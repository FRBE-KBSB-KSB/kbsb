# copyright Ruben Decrop 2012 - 2020
import logging
import json
from pathlib import Path
from datetime import datetime, date
from kbsb import settings
from kbsb.service.secrets import get_secret
import mysql.connector as mc


log = logging.getLogger("kbsb")


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

    if not hasattr(get_mongodb, "database"):
        mongoparams = get_secret("mongodb")
        loop = get_event_loop()
        client = AsyncIOMotorClient(mongoparams["url"], io_loop=loop)
        setattr(get_mongodb, "database", client[mongoparams["db"]])
    return get_mongodb.database


def get_mysql():
    """
    a singleton function to get the mongodb database asynchronously
    """
    if not hasattr(get_mysql, "conn"):
        mysqlparams = get_secret("mysql")
        try:
            conn = mc.connect(
                host=mysqlparams["dbhost"],
                user=mysqlparams["dbuser"],
                password=mysqlparams["dbpassword"],
                database=mysqlparams["dbname"],
                ssl_disabled=True,
            )
            setattr(get_mysql, "conn", conn)
        except mc.Error as e:
            log.error(f"Failed to set up Mysql connection: {e}")
            raise HTTPException(status_code=503, detail="CannotConnectMysql")
    return getattr(get_mysql, "conn")


# import all database classes

import kbsb.db.mysql_signaletique
