import asyncio
import logging
import xmlrpc.client
from datetime import datetime, timedelta, timezone

from reddevil.core import (
    # RdInternalServerError,
    RdNotAuthorized,
    # RdNotFound,
    get_setting,
    jwt_encode,
)

from kbsb.member import SALT

logger = logging.getLogger(__name__)
odoo_settings = get_setting("ODOO")
token_settings = get_setting("TOKEN")


async def odoo_login(idmember: int | str, password: str) -> str:
    if isinstance(idmember, int):
        idmember = str(idmember)
    url = odoo_settings["url"]
    db = odoo_settings["db"]
    logger.info(f"odoo_login: idmember {idmember} url {url} db {db}")
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, idmember, password, {})
    if not uid:
        logger.info(f"user empty: idmember {idmember} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    payload = {
        "sub": idmember,
        "exp": datetime.now(tz=timezone.utc)
        + timedelta(minutes=token_settings["timeout"]),
    }
    await asyncio.sleep(0)
    return jwt_encode(payload, SALT)


async def odoo_mgmt_getmember(idmember: int, password: str):
    pass


async def odoo_anon_getmember(idmember: int, password: str):
    pass


async def odoo_anon_getclubmembers(idclub: int):
    pass


async def odoo_mgmt_getclubmembers(idclub: int):
    pass


async def odoo_anon_belid_from_fideid():
    pass


async def odoo_anon_getfidemember():
    pass


async def odoo_old_userpassword():
    pass
