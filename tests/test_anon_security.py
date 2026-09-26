from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
import reddevil.core
from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from jose import jwt

_real_get_secret = reddevil.core.get_secret
reddevil.core.get_secret = lambda name: {} if name == "odoo" else _real_get_secret(name)

reddevil.core.register_app(FastAPI(), "kbsb.settings", "/api")

from reddevil.core import RdNotAuthorized, get_setting

from kbsb.club import Club, api_club, public_club
from kbsb.core import tokens
from kbsb.member.md_member import SALT

SECRET = get_setting("JWT_SECRET")


def token(sub, salt, key=None, minutes=30):
    payload = {"sub": sub, "exp": datetime.now(tz=UTC) + timedelta(minutes=minutes)}
    return jwt.encode(payload, (key or SECRET) + salt, "HS256")


def bearer(tok):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=tok)


class TestMemberToken:
    def test_a_token_the_site_signed_is_accepted(self):
        assert tokens.validate_membertoken(bearer(token("123456", SALT))) == "123456"

    def test_a_token_signed_with_another_key_is_refused(self):
        with pytest.raises(RdNotAuthorized):
            tokens.validate_membertoken(bearer(token("123456", SALT, key="guessed")))

    def test_an_unsigned_token_is_refused(self):
        forged = jwt.encode({"sub": "123456"}, "", "HS256")
        with pytest.raises(RdNotAuthorized):
            tokens.validate_membertoken(bearer(forged))

    def test_an_expired_token_is_refused(self):
        with pytest.raises(RdNotAuthorized) as e:
            tokens.validate_membertoken(bearer(token("123456", SALT, minutes=-1)))
        assert e.value.description == "TokenExpired"

    def test_no_token_is_refused(self):
        with pytest.raises(RdNotAuthorized):
            tokens.validate_membertoken(None)


class TestAdminToken:
    @pytest.mark.asyncio
    async def test_an_admin_token_with_its_account_salt_is_accepted(self):
        with patch.object(tokens, "get_tokensalt", AsyncMock(return_value="acct")):
            assert await tokens.validate_token(bearer(token("a@frbe-kbsb-ksb.be", "acct"))) == (
                "a@frbe-kbsb-ksb.be"
            )

    @pytest.mark.asyncio
    async def test_a_member_token_does_not_open_the_admin_api(self):
        with (
            patch.object(tokens, "get_tokensalt", AsyncMock(return_value=None)),
            pytest.raises(RdNotAuthorized),
        ):
            await tokens.validate_token(bearer(token("123456", SALT)))

    @pytest.mark.asyncio
    async def test_an_admin_token_signed_with_another_key_is_refused(self):
        with (
            patch.object(tokens, "get_tokensalt", AsyncMock(return_value="acct")),
            pytest.raises(RdNotAuthorized),
        ):
            await tokens.validate_token(bearer(token("a@frbe-kbsb-ksb.be", "acct", key="guessed")))

    @pytest.mark.asyncio
    async def test_a_superuser_token_is_accepted(self):
        with patch.object(tokens, "get_tokensalt", AsyncMock(return_value=None)):
            assert await tokens.validate_token(bearer(token("SU__ruben", SALT))) == "SU__ruben"


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


class TestPublicClub:
    def test_no_bank_account_admin_mail_roles_or_member_numbers(self):
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

    def test_board_contacts_only_where_public(self):
        board = public_club(stored_club()).boardmembers
        assert board["president"].email == "p@example.org"
        assert board["president"].mobile == "0470000000"
        assert board["treasurer"].email == "#NA"
        assert board["treasurer"].mobile == "#NA"
        assert board["secretary"].email == "#NA"
        assert board["secretary"].mobile == "#NA"
        assert board["treasurer"].first_name == "Hidden"

    def test_what_the_public_page_shows_is_still_there(self):
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


def test_the_club_csv_needs_an_admin():
    assert client.get("/api/v1/clubs/anon/csvclubs").status_code in (401, 403)
    with patch.object(tokens, "get_tokensalt", AsyncMock(return_value=None)):
        member = token("123456", SALT)
        resp = client.get(
            "/api/v1/clubs/anon/csvclubs", headers={"Authorization": f"Bearer {member}"}
        )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_a_second_admin_login_keeps_the_first_token_valid():
    import reddevil.account.account as rd_account

    import kbsb.main  # noqa: F401

    acc = {"id": "a@frbe-kbsb-ksb.be", "tokensalt": "acct"}
    with patch.object(rd_account, "update_account", AsyncMock()) as update:
        first = await rd_account.get_token(acc, timedelta(minutes=5))
        second = await rd_account.get_token(acc, timedelta(minutes=5))
    update.assert_not_called()
    assert rd_account.login.__globals__["get_token"] is rd_account.get_token
    with patch.object(tokens, "get_tokensalt", AsyncMock(return_value="acct")):
        assert await tokens.validate_token(bearer(first)) == "a@frbe-kbsb-ksb.be"
        assert await tokens.validate_token(bearer(second)) == "a@frbe-kbsb-ksb.be"


# -- who may see or change what, once logged in -------------------------------

from kbsb.core import RdForbidden
from kbsb.interclubs import api_interclubs
from kbsb.interclubs.md_interclubs import ICSeries
from kbsb.member import api_member

full = FastAPI()
full.include_router(api_club.router)
full.include_router(api_member.router)
full.include_router(api_interclubs.router)
member_client = TestClient(full)


def as_member(idnumber):
    return {"Authorization": f"Bearer {token(str(idnumber), SALT)}"}


def test_the_full_club_record_is_only_for_that_clubs_admin():
    with patch("kbsb.club.api_club.verify_club_access", AsyncMock(side_effect=RdForbidden)):
        assert member_client.get("/api/v1/clubs/clb/club/195", headers=as_member(1)).status_code == 403
    with (
        patch("kbsb.club.api_club.verify_club_access", AsyncMock(return_value=True)),
        patch("kbsb.club.api_club.get_club", AsyncMock(return_value=stored_club())),
    ):
        assert member_client.get("/api/v1/clubs/clb/club/195", headers=as_member(1)).status_code == 200


def test_a_member_sees_only_their_own_details():
    with patch("kbsb.member.api_member.mgmt_getmember", AsyncMock(return_value={"idnumber": 1})):
        assert member_client.get("/api/v1/member/clb/member/2", headers=as_member(1)).status_code == 403
        assert member_client.get("/api/v1/member/clb/member/1", headers=as_member(1)).status_code == 200


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
        resp = member_client.put("/api/v1/interclubs/clb/icplanning", json=planning, headers=as_member(1))
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
