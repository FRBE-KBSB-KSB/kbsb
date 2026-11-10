"""The member lookups must only ask Odoo for fields it has.

Odoo answers an unknown field with an error object instead of a list, which
turned every club's player list into a 500 once x_studio_contact_clubid_link
was removed from res.partner.
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from kbsb.member import member

REMOVED = "x_studio_contact_clubid_link"

ROW = {
    "id": 1,
    "email_normalized": "a@example.org",
    "phone_sanitized": "",
    "x_studio_contact_affiliationyear": 2027,
    "x_studio_contact_birthday_date": "2001-02-03",
    "x_studio_contact_fideid_int": 5,
    "x_studio_contact_fidenat_id": [1, "BEL Belgium"],
    "x_studio_contact_fidetitle": False,
    "x_studio_contact_firstname": "Ann",
    "x_studio_contact_gender": "F",
    "x_studio_contact_name": "Doe",
    "x_studio_contact_nationalid_int": 12345,
    "parent_id": [472, "Some Club"],
    "x_studio_contact_clubid": 472,
}


def odoo(seen):
    def handler(request):
        payload = json.loads(request.content)
        seen.append(payload)
        # Odoo's reply to a field it does not have
        if REMOVED in payload.get("fields", []) or any(
            REMOVED in str(term) for term in payload.get("domain", [])
        ):
            return httpx.Response(500, json={"name": "builtins.ValueError"})
        return httpx.Response(200, json=[ROW])

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.mark.asyncio
async def test_the_club_lists_name_the_club_they_were_asked_for():
    seen = []
    with (
        patch.object(member, "_get_extra_asynclient", lambda: odoo(seen)),
        patch.object(member, "get_fideelo", AsyncMock(return_value=1500)),
    ):
        anon = await member.anon_getclubmembers(472)
        mgmt = await member.mgmt_getclubmembers(472)
    assert [a.idclub for a in anon] == [472]
    assert [a.idclub for a in mgmt] == [472]
    assert all(REMOVED not in str(p) for p in seen)


@pytest.mark.asyncio
async def test_a_single_member_finds_its_club_through_its_parent():
    seen = []
    with (
        patch.object(member, "_get_extra_asynclient", lambda: odoo(seen)),
        patch.object(member, "get_fideelo", AsyncMock(return_value=1500)),
    ):
        found = await member.mgmt_getmember(12345)
    assert found.idclub == 472
    assert all(REMOVED not in str(p) for p in seen)


@pytest.mark.asyncio
async def test_a_member_without_a_club_has_club_zero():
    assert await member._club_id_of_partner(False) == 0
