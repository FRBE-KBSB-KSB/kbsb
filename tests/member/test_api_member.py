from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from reddevil.core import RdNotAuthorized, RdNotFound

from kbsb.main import app


@patch("kbsb.member.api_member.anon_getmember")
def test_anon_getmember(anon_getmember: AsyncMock, anon_member_factory):
    client = TestClient(app)
    anon_getmember.return_value = anon_member_factory.build()
    resp = client.get("/api/v1/member/anon/member/45608")
    reply = resp.json()
    assert resp.status_code == 200
    assert "birthyear" in reply
    anon_getmember.assert_awaited()


@pytest.mark.skip(reason="API endpoint no longer available")
@patch("kbsb.member.api_member.anon_getfidemember", create=True)
def test_anon_getfidemember(anon_getmember: AsyncMock, anon_member_factory):
    client = TestClient(app)
    anon_getmember.return_value = anon_member_factory.build()
    resp = client.get("/api/v1/member/anon/fidemember/201308")
    reply = resp.json()
    assert resp.status_code == 200
    assert "birthyear" in reply
    anon_getmember.assert_awaited()


@patch("kbsb.member.api_member.mgmt_getmember")
@patch("kbsb.member.api_member.validate_header_incoming")
def test_incoming_get_member_success(
    mock_validate_header: MagicMock,
    mock_mgmt_getmember: AsyncMock,
    member_factory,
):
    client = TestClient(app)
    expected_member = member_factory.build(idnumber=45608)
    mock_mgmt_getmember.return_value = expected_member

    resp = client.get(
        "/api/v1/member/incoming/my-domain/member/45608",
        headers={"X-API-Key": "test-key"},
    )
    assert resp.status_code == 200
    reply = resp.json()
    assert reply["idnumber"] == 45608
    assert reply["first_name"] == expected_member.first_name
    assert reply["last_name"] == expected_member.last_name
    mock_validate_header.assert_called_once_with("test-key", "my-domain")
    mock_mgmt_getmember.assert_awaited_once_with(45608)


def test_incoming_get_member_missing_api_key():
    client = TestClient(app)
    resp = client.get("/api/v1/member/incoming/my-domain/member/45608")
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


@patch("kbsb.member.api_member.mgmt_getmember")
@patch("kbsb.member.api_member.validate_header_incoming")
def test_incoming_get_member_invalid_api_key(
    mock_validate_header: MagicMock,
    mock_mgmt_getmember: AsyncMock,
):
    client = TestClient(app)
    mock_validate_header.side_effect = RdNotAuthorized(
        description="InvalidIncomingServerKey"
    )

    resp = client.get(
        "/api/v1/member/incoming/my-domain/member/45608",
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "InvalidIncomingServerKey"}
    mock_mgmt_getmember.assert_not_called()


@patch("kbsb.member.api_member.mgmt_getmember")
@patch("kbsb.member.api_member.validate_header_incoming")
def test_incoming_get_member_not_found(
    mock_validate_header: MagicMock,
    mock_mgmt_getmember: AsyncMock,
):
    client = TestClient(app)
    mock_mgmt_getmember.side_effect = RdNotFound(description="MemberNotFound")

    resp = client.get(
        "/api/v1/member/incoming/my-domain/member/99999",
        headers={"X-API-Key": "test-key"},
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "MemberNotFound"}
    mock_validate_header.assert_called_once_with("test-key", "my-domain")
    mock_mgmt_getmember.assert_awaited_once_with(99999)

