import io
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import reddevil.core
from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from jose import jwt
from reddevil.core import RdNotAuthorized, get_setting

from kbsb.club import Club, api_club, public_club
from kbsb.core import RdForbidden, tokens
from kbsb.core.tokens import get_salt
from kbsb.interclubs import api_interclubs
from kbsb.interclubs.md_interclubs import ICSeries
from kbsb.member import Login2FaValidator, LoginReply, api_member, login2FA

reddevil.core.register_app(FastAPI(), "kbsb.settings", "/api")

jwt_secret = get_setting("JWT")["secret"]
jwt_algorithm = get_setting("JWT")["algorithm"]
salt = get_salt()
member_salt = tokens.get_member_salt()


def token(sub, salt, key=None, minutes=30):
    payload = {"sub": sub, "exp": datetime.now(tz=UTC) + timedelta(minutes=minutes)}
    return jwt.encode(payload, (key or jwt_secret) + salt, jwt_algorithm)


def bearer(tok):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok)


def test_a_token_the_site_signed_is_accepted():
    assert tokens.validate_membertoken(bearer(token("123456", member_salt))) == "123456"


def test_a_token_signed_with_another_key_is_refused():
    with pytest.raises(RdNotAuthorized):
        tokens.validate_membertoken(bearer(token("123456", member_salt, key="guessed")))


def test_an_unsigned_token_is_refused():
    forged = jwt.encode({"sub": "123456"}, "", "HS256")
    with pytest.raises(RdNotAuthorized):
        tokens.validate_membertoken(bearer(forged))


def test_an_expired_token_is_refused():
    with pytest.raises(RdNotAuthorized) as e:
        tokens.validate_membertoken(bearer(token("123456", member_salt, minutes=-1)))
    assert e.value.description == "TokenExpired"


def test_no_token_is_refused():
    with pytest.raises(RdNotAuthorized):
        tokens.validate_membertoken(None)


@pytest.mark.asyncio
async def test_an_admin_token_with_its_account_salt_is_accepted():
    with patch.object(tokens, "get_tokensalt", AsyncMock(return_value="acct")):
        assert await tokens.validate_token(
            bearer(token("a@frbe-kbsb-ksb.be", "acct"))
        ) == ("a@frbe-kbsb-ksb.be")


@pytest.mark.asyncio
async def test_a_member_token_does_not_open_the_admin_api():
    # signed the way login signs it, with the real salts and nothing patched
    with pytest.raises(RdNotAuthorized):
        await tokens.validate_token(bearer(token("123456", member_salt)))


@pytest.mark.asyncio
async def test_an_admin_token_signed_with_another_key_is_refused():
    with (
        patch.object(tokens, "get_tokensalt", AsyncMock(return_value="acct")),
        pytest.raises(RdNotAuthorized),
    ):
        await tokens.validate_token(
            bearer(token("a@frbe-kbsb-ksb.be", "acct", key="guessed"))
        )


@pytest.mark.asyncio
async def test_a_superuser_token_is_accepted():
    ruben = await tokens.validate_token(bearer(token("SU__ruben", salt)))
    assert ruben == "SU__ruben"


def stored_club():
    return Club.model_validate(
        {
            "idclub": 195,
            "name_short": "KOSK",
            "name_long": "Koninklijke Schaakkring",
            "address": "Straat 1, 2000 Antwerpen",
            "venue": "Zaal",
            "website": "https://example.org",
            "email_main": "info@example.org",
            "email_interclub": "ic@example.org",
            "email_admin": "admin@example.org",
            "email_finance": "finance@example.org",
            "bankaccount_name": "KOSK vzw",
            "bankaccount_iban": "BE68539007547034",
            "bankaccount_bic": "GKCCBEBB",
            "clubroles": [{"nature": "ClubAdmin", "memberlist": [101, 102]}],
            "boardmembers": {
                "president": {
                    "first_name": "Public",
                    "last_name": "Person",
                    "idnumber": 101,
                    "email": "p@example.org",
                    "email_visibility": "PUBLIC",
                    "mobile": "0470000000",
                    "mobile_visibility": "PUBLIC",
                },
                "treasurer": {
                    "first_name": "Hidden",
                    "last_name": "Person",
                    "idnumber": 102,
                    "email": "h@example.org",
                    "email_visibility": "HIDDEN",
                    "mobile": "0471111111",
                    "mobile_visibility": "CLUB",
                },
                "secretary": {
                    "first_name": "Unset",
                    "last_name": "Person",
                    "idnumber": 103,
                    "email": "u@example.org",
                    "mobile": "0472222222",
                },
            },
        }
    )


def test_no_bank_account_admin_mail_roles_or_member_numbers():
    out = public_club(stored_club()).model_dump()
    text = str(out)
    for secret in [
        "BE68539007547034",
        "GKCCBEBB",
        "KOSK vzw",
        "admin@example.org",
        "finance@example.org",
    ]:
        assert secret not in text
    assert "clubroles" not in out
    assert all("idnumber" not in bm for bm in out["boardmembers"].values())


def test_board_contacts_only_where_public():
    board = public_club(stored_club()).boardmembers
    assert board["president"].email == "p@example.org"
    assert board["president"].mobile == "0470000000"
    assert board["treasurer"].email == "#NA"
    assert board["treasurer"].mobile == "#NA"
    assert board["secretary"].email == "#NA"
    assert board["secretary"].mobile == "#NA"
    assert board["treasurer"].first_name == "Hidden"


def test_what_the_public_page_shows_is_still_there():
    out = public_club(stored_club())
    assert out.name_long == "Koninklijke Schaakkring"
    assert out.address == "Straat 1, 2000 Antwerpen"
    assert out.email_main == "info@example.org"
    assert out.email_interclub == "ic@example.org"
    assert out.website == "https://example.org"


app = FastAPI()
app.include_router(api_club.router)
client = TestClient(app)


def test_the_public_route_serves_the_public_view():
    with patch("kbsb.club.club.get_club", AsyncMock(return_value=stored_club())):
        resp = client.get("/api/v1/clubs/anon/club/195")
    assert resp.status_code == 200
    body = resp.json()
    assert "bankaccount_iban" not in body
    assert "BE68539007547034" not in resp.text
    assert body["boardmembers"]["treasurer"]["email"] == "#NA"


@patch("kbsb.club.api_club.get_csv_clubs")
def test_the_club_csv_needs_an_admin(get_csv_clubs):
    get_csv_clubs.return_value = io.StringIO("a,b\nAA,BB\nCC,DD")
    assert client.get("/api/v1/clubs/anon/csvclubs").status_code in (401, 403)
    admin = token("SU__ruben", salt)
    resp = client.get(
        "/api/v1/clubs/anon/csvclubs", headers={"Authorization": f"Bearer {admin}"}
    )
    assert resp.status_code == 200
    member = token("123456", member_salt)
    resp = client.get(
        "/api/v1/clubs/anon/csvclubs", headers={"Authorization": f"Bearer {member}"}
    )
    assert resp.status_code == 401


# -- who may see or change what, once logged in -------------------------------


full = FastAPI()
full.include_router(api_club.router)
full.include_router(api_member.router)
full.include_router(api_interclubs.router)
member_client = TestClient(full)


def as_member(idnumber):
    return {"Authorization": f"Bearer {token(str(idnumber), member_salt)}"}


def test_the_full_club_record_is_only_for_that_clubs_admin():
    with patch(
        "kbsb.club.api_club.verify_club_access", AsyncMock(side_effect=RdForbidden)
    ):
        assert (
            member_client.get(
                "/api/v1/clubs/clb/club/195", headers=as_member(1)
            ).status_code
            == 403
        )
    with (
        patch("kbsb.club.api_club.verify_club_access", AsyncMock(return_value=True)),
        patch("kbsb.club.api_club.get_club", AsyncMock(return_value=stored_club())),
    ):
        assert (
            member_client.get(
                "/api/v1/clubs/clb/club/195", headers=as_member(1)
            ).status_code
            == 200
        )


def test_a_member_sees_only_their_own_details():
    with patch(
        "kbsb.member.api_member.mgmt_getmember", AsyncMock(return_value={"idnumber": 1})
    ):
        assert (
            member_client.get(
                "/api/v1/member/clb/member/2", headers=as_member(1)
            ).status_code
            == 403
        )
        assert (
            member_client.get(
                "/api/v1/member/clb/member/1", headers=as_member(1)
            ).status_code
            == 200
        )


def test_the_mailinglist_refuses_a_made_up_admin_token():
    forged = token("anyone@frbe-kbsb-ksb.be", "whatever", key="guessed")
    with patch.object(tokens, "get_tokensalt", AsyncMock(return_value="acct")):
        resp = member_client.get(f"/api/v1/clubs/mgmt/mailinglist?token={forged}")
    assert resp.status_code == 401


def test_a_line_up_for_another_club_is_refused():
    planning = {"idclub": 195, "round": 1, "plannings": []}
    with (
        patch("kbsb.club.verify_club_access", AsyncMock(side_effect=RdForbidden)),
        patch("kbsb.interclubs.api_interclubs.clb_saveICplanning", AsyncMock()) as save,
    ):
        resp = member_client.put(
            "/api/v1/interclubs/clb/icplanning", json=planning, headers=as_member(1)
        )
    assert resp.status_code == 403
    save.assert_not_called()


@pytest.mark.asyncio
async def test_other_clubs_line_ups_are_hidden_before_the_round():
    series = ICSeries.model_validate(
        {
            "division": 2,
            "index": "A",
            "teams": [],
            "rounds": [
                {
                    "round": 1,
                    "rdate": "2026-10-04",
                    "encounters": [
                        {
                            "icclub_home": 195,
                            "icclub_visit": 108,
                            "pairingnr_home": 1,
                            "pairingnr_visit": 2,
                            "games": [{"idnumber_home": 11, "idnumber_visit": 22}],
                        },
                        {
                            "icclub_home": 209,
                            "icclub_visit": 301,
                            "pairingnr_home": 3,
                            "pairingnr_visit": 4,
                            "games": [{"idnumber_home": 33, "idnumber_visit": 44}],
                        },
                    ],
                }
            ],
        }
    )
    with patch("kbsb.interclubs.series.isRoundOpen", AsyncMock(return_value=False)):
        [out] = await api_interclubs._hide_other_lineups([series], 195)
    own, other = out.rounds[0].encounters
    assert (own.games[0].idnumber_home, own.games[0].idnumber_visit) == (11, 0)
    assert (other.games[0].idnumber_home, other.games[0].idnumber_visit) == (0, 0)


# -- member tokens are not admin tokens ---------------------------------------


@pytest.mark.asyncio
async def test_a_member_number_is_never_an_admin_whatever_it_was_signed_with():
    with pytest.raises(RdNotAuthorized):
        await tokens.validate_token(bearer(token("123456", salt)))


def test_an_admin_token_is_not_a_member_token():
    with pytest.raises(RdNotAuthorized):
        tokens.validate_membertoken(bearer(token("a@frbe-kbsb-ksb.be", salt)))


def test_a_superuser_token_still_works_on_the_member_routes():
    sub = tokens.validate_membertoken(bearer(token("SU__ruben", salt)))
    assert sub == "SU__ruben"


# -- the 2FA step belongs to the account that passed the password step --------


def odoo_2fa_client(accepts=True):
    def handler(request):
        if accepts:
            return httpx.Response(303, headers={"location": "/my"})
        return httpx.Response(200, text="wrong code")

    return httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://odoo.test"
    )


def second_step(**changes):
    fields = {
        "csrf": "c",
        "code2FA": "123456",
        "session_id": "sess",
        "state": tokens.issue_2fa_state("me@example.org", "sess"),
    }
    return Login2FaValidator(**{**fields, **changes})


@pytest.mark.asyncio
async def test_the_2fa_token_is_for_the_account_that_passed_the_password_step():
    member_number = AsyncMock(return_value=111)
    with patch("kbsb.member.member.odoo_member_number", member_number):
        # the email the browser sends is somebody else's
        reply = await login2FA(
            second_step(email="victim@example.org"), odoo_2fa_client()
        )
    assert member_number.await_args.args[0] == "me@example.org"
    assert tokens.validate_membertoken(bearer(reply.jwttoken)) == "111"


@pytest.mark.asyncio
async def test_a_2fa_state_cannot_be_used_with_another_odoo_session():
    with pytest.raises(RdNotAuthorized):
        await login2FA(second_step(session_id="someone-elses"), odoo_2fa_client())


@pytest.mark.asyncio
async def test_a_forged_2fa_state_is_refused():
    forged = jwt.encode(
        {
            "sub": "victim@example.org",
            "sid": "sess",
            "exp": datetime.now(tz=UTC) + timedelta(minutes=5),
        },
        jwt_secret + salt,
        jwt_algorithm,
    )
    for state in ("garbage", forged):
        with pytest.raises(RdNotAuthorized):
            await login2FA(second_step(state=state), odoo_2fa_client())


@pytest.mark.asyncio
async def test_an_old_2fa_state_is_refused():
    with patch.object(tokens, "STATE_2FA_MINUTES", -1):
        state = tokens.issue_2fa_state("me@example.org", "sess")
    with pytest.raises(RdNotAuthorized):
        await login2FA(second_step(state=state), odoo_2fa_client())


@pytest.mark.asyncio
async def test_a_wrong_2fa_code_gives_no_token():
    with (
        patch("kbsb.member.member.odoo_member_number", AsyncMock(return_value=111)),
        pytest.raises(RdNotAuthorized),
    ):
        await login2FA(second_step(), odoo_2fa_client(accepts=False))


# -- the Odoo login sessions ----------------------------------------------------


@pytest.mark.asyncio
async def test_every_request_gets_its_own_odoo_client():
    first, second = api_member.get_odoo_client(), api_member.get_odoo_client()
    one, two = await anext(first), await anext(second)
    one.cookies.set("session_id", "belongs-to-one")
    assert one is not two
    assert two.cookies.get("session_id") is None
    await first.aclose()
    await second.aclose()


# -- the tournament dashboard's Odoo login -------------------------------------


@pytest.mark.asyncio
async def test_odoo_login_gives_the_member_number():
    from kbsb.member.member import odoo_login

    member_token = jwt.encode(
        {"sub": "777", "exp": datetime.now(tz=UTC) + timedelta(minutes=5)},
        jwt_secret + member_salt,
        jwt_algorithm,
    )
    reply = LoginReply(id=1, jwttoken=member_token)
    with patch("kbsb.member.login.login", AsyncMock(return_value=reply)):
        assert await odoo_login("me@example.org", "pw") == (777, member_token)


@pytest.mark.asyncio
async def test_odoo_login_refuses_2fa_accounts_and_superusers():
    from kbsb.member.member import odoo_login

    asks_2fa = LoginReply(id=-1, is2FAneeded=True, session_id="s", csrf="c")
    with (
        patch("kbsb.member.login.login", AsyncMock(return_value=asks_2fa)),
        pytest.raises(RdNotAuthorized),
    ):
        await odoo_login("me@example.org", "pw")
    with pytest.raises(RdNotAuthorized):
        await odoo_login("SU__ruben", "pw")


# -- which member has logged in -----------------------------------------------


def odoo_session_client(partner_id=None):
    def handler(request):
        assert request.headers["cookie"] == "session_id=sess"
        return httpx.Response(200, json={"result": {"partner_id": partner_id}})

    return httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://odoo.test"
    )


@pytest.mark.asyncio
async def test_the_member_is_the_partner_of_the_session_not_whoever_shares_the_email():
    from kbsb.member.member import odoo_member_number

    lookup = AsyncMock(return_value=19833)
    with patch("kbsb.member.member.odoo_email2idbel", lookup):
        number = await odoo_member_number(
            "family@example.org", odoo_session_client(183705), "sess"
        )
    assert number == 19833
    lookup.assert_awaited_once_with("family@example.org", partner_id=183705)


@pytest.mark.asyncio
async def test_without_a_session_partner_a_single_email_match_is_used():
    from kbsb.member.member import odoo_member_number

    lookup = AsyncMock(return_value=19833)
    with patch("kbsb.member.member.odoo_email2idbel", lookup):
        number = await odoo_member_number(
            "me@example.org", odoo_session_client(None), "sess"
        )
    assert number == 19833
    lookup.assert_awaited_once_with("me@example.org")


@pytest.mark.asyncio
async def test_no_or_several_email_matches_is_a_refusal_not_a_server_error():
    from kbsb.member.member import odoo_member_number

    lookup = AsyncMock(side_effect=RuntimeError("Odoo search_read failed"))
    with (
        patch("kbsb.member.member.odoo_email2idbel", lookup),
        pytest.raises(RdNotAuthorized),
    ):
        await odoo_member_number("me@example.org", odoo_session_client(None), "sess")


@pytest.mark.asyncio
async def test_odoo_failing_to_name_the_session_falls_back_to_the_email():
    from kbsb.member.member import odoo_member_number

    def broken(request):
        return httpx.Response(500, text="boom")

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(broken), base_url="https://odoo.test"
    )
    lookup = AsyncMock(return_value=19833)
    with patch("kbsb.member.member.odoo_email2idbel", lookup):
        assert await odoo_member_number("me@example.org", client, "sess") == 19833
