# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2026

# This module performs a login on the Odoo system
# It supports 2FA
# As a general rule, the module simulates the loading and processing
# of the https://frbe-kbsb.odoo.com/web/login page.
# In case a user has enabled 2FA, this a 2 phase approach, where the 2FA
# code is processed in the 2nd phase.
# To detect if a user has 2FA enabled, we check if after the login of
# the https://frbe-kbsb.odoo.com/web/login page, the user is redirectred
# to the https://frbe-kbsb.odoo.com/web/login/totp page.
# In other words this is a hacky solution, that requires maintenance

import logging
import re
from datetime import UTC, datetime, timedelta

import httpx
from reddevil.core import (  # type: ignore[import-untyped]
    RdException,
    RdNotAuthorized,
    get_secret,
    get_setting,
    jwt_encode,
)

from kbsb.core.tokens import (
    get_member_salt,
    get_salt,
    issue_2fa_state,
    read_2fa_state,
)

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
    except Exception:
        logger.exception("Superuser login failed")
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

    # we are simulating the login page on odoo
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

    # we perform a POST in the login page actually performing a login
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
    logger.info(
        f"after login {response2.status_code} {response2.headers.get('location', '')}"
    )
    session_id = response2.cookies.get("session_id") or ""

    # if we are redirected to the /web/login/totp , 2FA is active
    if response2.status_code == 303 and "/web/login/totp" in response2.headers.get(
        "location", ""
    ):
        # load the 2FA page
        response3 = await odoo_client.get(
            "/web/login/totp", cookies={"session_id": session_id}
        )
        if response3.status_code >= 400:
            raise RdException(
                status_code=response3.status_code,
                description="CannotLoadOdooLogin2FAPage",
            )

        # we need the csrf token and the session_id in the subsequent
        # api_login2fa call
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response3.text)
        if not csrf_match:
            raise RuntimeError("Could not find CSRF token on the /web/login/totp page")
        csrf = csrf_match.group(1)
        return LoginReply(
            id=-1,
            csrf=csrf,
            is2FAneeded=True,
            session_id=session_id,
            state=issue_2fa_state(ol.email, session_id),
        )

    # login successfull but 2FA not active, so we return JWT token
    if response2.status_code == 303 and "/my" in response2.headers.get("location", ""):
        idbel = await odoo_email2idbel(ol.email)
        logger.info(f"{idbel} succesfully logged in without 2FA")
        payload = {
            "sub": str(idbel),
            "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
        }
        return LoginReply(id=1, jwttoken=jwt_encode(payload, get_member_salt()))
    # login unseccessful
    raise RdNotAuthorized()


async def login2FA(
    l2fa: Login2FaValidator, odoo_client: httpx.AsyncClient
) -> LoginReply:
    """
    performs the 2nd fase in a 2FA login process
    """

    from .member import odoo_email2idbel

    # whose login this is comes from what the server signed in the first step,
    # never from the request: Odoo only says that *some* account passed 2FA
    email = read_2fa_state(l2fa.state, l2fa.session_id)

    # posting on the 2FA page, submitting the 2FA code
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
    # If we are redirected to the /my page, the 2FA is handled successfully
    if response.status_code == 303 and "/my" in response.headers.get("location", ""):
        idbel = await odoo_email2idbel(email)
        logger.info(f"{idbel} succesfully logged in with 2FA")
        payload = {
            "sub": str(idbel),
            "exp": datetime.now(tz=UTC) + timedelta(minutes=token_settings["timeout"]),
        }
        return LoginReply(id=1, jwttoken=jwt_encode(payload, get_member_salt()))

    # if not raise not authorized
    raise RdNotAuthorized
