# copyright Ruben Decrop 2012 - 2020
import logging
from datetime import date, datetime

from reddevil.core import get_secret

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


def get_odoo():
    """
    Setup the Odoo database connection.
    """
    if not hasattr(get_odoo, "secrets"):
        get_odoo.secrets = get_secret("odoo")  # type: ignore
    return get_odoo.secrets  # type: ignore
