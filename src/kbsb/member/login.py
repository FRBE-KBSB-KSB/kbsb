# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
import re
from datetime import UTC, datetime, timedelta

import httpx
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import (
    RdException,
    RdNotAuthorized,
    get_secret,
    get_setting,
    jwt_encode,
)

from .md_member import (
    Login2FAValidator,
    LoginReply,
    LoginValidator,
)

logger = logging.getLogger(__name__)
token_settings = get_setting("TOKEN")
salt = get_setting("SALT")


async def superuser_login(superid: str, password: str) -> str:
    """
    Performs a superuser login with the password stored in GCP secret manager
    returns a JWT token
    """
    token_settings = get_setting("TOKEN")
    try:
        su = get_secret(superid)
        if su.get("password") != password:
            raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    except Exception as e:
        logger.exception(f"Superuser login failed: {e}")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    payload = {
        "sub": superid,
        "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
    }
    return jwt_encode(payload, salt)


async def login(ol: LoginValidator, odoo_client: httpx.AsyncClient) -> LoginReply:
    """
    Do a login based on email and password
    if successful returns a JWT token
    if 2FA is activated on the account, is2FAneeded is set as True, and the user must
       provide the 2FA token in the login2FA method, where the JWT token can be returned
    """
    if ol.email.startswith("SU__"):
        return LoginReply(id=0, jwttoken=await superuser_login(ol.email, ol.password))
    # we are requesting the login page on odoo, which is a kind of hack
    response = await odoo_client.get("/web/login")
    if response.status_code >= 400:
        raise RdException(
            status_code=response.status_code, description="CannotReachOdooLoginPage"
        )
    logger.info("called Odoo /web/login")
    # we need the csrf token of the login page
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if not csrf_match:
        raise RuntimeError("Could not find CSRF token on the /web/login page")
    csrf_token = csrf_match.group(1)
    # we perform a POST in the login page
    response = await odoo_client.post(
        "/web/login",
        data={
            "login": ol.email,
            "password": ol.password,
            "csrf_token": csrf_token,
            "db": get_setting("ODOO")["db"],
        },
    )
    if response.status_code >= 400:
        raise RdException(
            status_code=response.status_code, description="CannotPostOdooLoginPage"
        )
    # if we are redirected to the /web/login/totp , 2FA is active
    if "/web/login/totp" in str(response.url):
        # we need the csrf token in the subsequent login2FA call
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if not csrf_match:
            raise RuntimeError("Could not find CSRF token on the /web/login/totp page")
        csrf_token = csrf_match.group(1)
        return LoginReply(id=-1, csrf=csrf_token, is2FAneeded=True)
    # create JWT token and return it
    payload = {
        "sub": "1",
        "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
    }
    return LoginReply(id=1, jwttoken=jwt_encode(payload, salt))


async def login2FA(
    l2fa: Login2FAValidator, odoo_client: httpx.AsyncClient
) -> LoginReply:
    """
    return a JWT token
    """
    logger.info("called Odoo /web/login/totp")
    response = await odoo_client.post(
        "/web/login/totp",
        data={
            "totp_token": l2fa.code2FA.strip(),
            "csrf_token": l2fa.csrf,
        },
    )
    if response.status_code >= 400:
        raise RdException(
            status_code=response.status_code, description="CannotPostOdooLogin2FA"
        )
    payload = {
        "sub": "1",
        "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
    }
    return LoginReply(id=1, jwttoken=jwt_encode(payload, salt))


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> str:
    """
    checks a JWT token for validity
    return an str with the if of the member if the token is correctly validated,
    if token validation fails, the function raises RdNotAuthorized

    """
    from kbsb.core.tokens import validate_membertoken as verified

    return verified(auth)
