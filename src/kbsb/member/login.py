# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
import re
from datetime import UTC, datetime, timedelta

import httpx
from reddevil.core import (
    RdException,
    RdNotAuthorized,
    get_secret,
    get_setting,
    jwt_encode,
)

from kbsb.core.tokens import get_salt

from .md_member import (
    Login2FaValidator,
    LoginReply,
    LoginValidator,
)

logger = logging.getLogger(__name__)
token_settings = get_setting("TOKEN")
odoo_params = get_setting("ODOO_CONNECTION_PARAMETERS")


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
    return jwt_encode(payload, get_salt())


async def login(ol: LoginValidator, odoo_client: httpx.AsyncClient) -> LoginReply:
    """
    Do a login based on email and password
    if successful returns a JWT token
    if 2FA is activated on the account, is2FAneeded is set as True, and the user must
       provide the 2FA token in the login2FA method, where the JWT token can be returned
    """
    from .member import odoo_email2idbel

    logger.info(f"logging in {ol.email}")
    if ol.email.startswith("SU__"):
        return LoginReply(id=0, jwttoken=await superuser_login(ol.email, ol.password))
    # we are requesting the login page on odoo, which is a kind of hack
    response1 = await odoo_client.get("/web/login")
    if response1.status_code >= 400:
        raise RdException(
            status_code=response1.status_code, description="CannotLoadOdooLoginPage"
        )
    # we need the csrf token of the login page
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response1.text)
    if not csrf_match:
        raise RuntimeError("Could not find CSRF token on the /web/login page")
    csrf = csrf_match.group(1)
    # we perform a POST in the login page
    response2 = await odoo_client.post(
        "/web/login",
        data={
            "login": ol.email,
            "password": ol.password,
            "csrf_token": csrf,
            "db": odoo_params["db"],
        },
    )
    if response2.status_code >= 400:
        raise RdException(
            status_code=response2.status_code, description="CannotPostOdooLoginPage"
        )
    session_id = response2.cookies.get("session_id") or ""
    # if we are redirected to the /web/login/totp , 2FA is active
    if response2.status_code == 303 and "/web/login/totp" in response2.headers.get(
        "location", ""
    ):
        response3 = await odoo_client.get(
            "/web/login/totp", cookies={"session_id": session_id}
        )
        if response3.status_code >= 400:
            raise RdException(
                status_code=response3.status_code,
                description="CannotLoadOdooLogin2FAPage",
            )
        # we need the csrf token and the session_id in the subsequent login2fa call
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response3.text)
        if not csrf_match:
            raise RuntimeError("Could not find CSRF token on the /web/login/totp page")
        csrf = csrf_match.group(1)
        return LoginReply(id=-1, csrf=csrf, is2FAneeded=True, session_id=session_id)
    # 2FA not active, so we return JWT token
    idbel = await odoo_email2idbel(ol.email)
    logger.info(f"{idbel} succesfully logged in without 2FA")
    payload = {
        "sub": str(idbel),
        "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
    }
    return LoginReply(id=1, jwttoken=jwt_encode(payload, get_salt()))


async def login2FA(
    l2fa: Login2FaValidator, odoo_client: httpx.AsyncClient
) -> LoginReply:
    """
    performs the 2nd fase in a 2FA login process
    """

    from .member import odoo_email2idbel

    logger.info("posting totp code to  Odoo /web/login/totp")
    response = await odoo_client.post(
        "/web/login/totp",
        data={
            "totp_token": l2fa.code2FA.strip(),
            "csrf_token": l2fa.csrf,
            "redirect": "/my",
        },
        cookies={"session_id": l2fa.session_id},
    )

    if response.status_code >= 400:
        raise RdException(
            status_code=response.status_code, description="CannotPostOdooLogin2FA"
        )
    logger.info(f"2fa response {response.status_code} ")
    if response.status_code == 303 and "/my" in response.headers.get("location", ""):
        # if odoo redirects the 2fa call was successfull
        idbel = await odoo_email2idbel(l2fa.email)
        logger.info(f"{idbel} succesfully logged in with 2FA")
        payload = {
            "sub": str(idbel),
            "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
        }
        return LoginReply(id=1, jwttoken=jwt_encode(payload, get_salt()))
    raise RdNotAuthorized
