# copyright Ruben Decrop 2012 - 2020
import logging
from datetime import date, datetime

import mysql.connector
from reddevil.core import RdInternalServerError, get_secret

logger = logging.getLogger(__name__)


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


def get_mysql():
    if not hasattr(get_mysql, "params"):
        setattr(get_mysql, "params", get_secret("mysql"))
    logger.debug(f"mysql host: {get_mysql.params['dbhost']}")  # type: ignore
    try:
        cnx = mysql.connector.connect(
            pool_name="kbsbpool",
            pool_size=5,
            user=get_mysql.params["dbuser"],  # type: ignore
            password=get_mysql.params["dbpassword"],  # type: ignore
            host=get_mysql.params["dbhost"],  # type: ignore
            database=get_mysql.params["dbname"],  # type: ignore
            ssl_disabled=True,
        )
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:  # type: ignore
            logger.exception("Something is wrong with your user name or password")
            raise RdInternalServerError(description="Invalid DB credentials")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:  # type: ignore
            logger.exception("Database does not exist")
            raise RdInternalServerError(description="Invalid DB")
        else:
            logger.exception(err)
            raise RdInternalServerError(description="Unknown DB error")
    except Exception as e:
        logger.exception(e)
        raise RdInternalServerError(description="Unknown DB error")
    return cnx


def get_odoo():
    """
    Setup the Odoo database connection.
    """
    if not hasattr(get_odoo, "secrets"):
        get_odoo.secrets = get_secret("odoo")  # type: ignore
    return get_odoo.secrets  # type: ignore
