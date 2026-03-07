import pytest  # noqa F401

from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
# from fastapi.encoders import jsonable_encoder

from kbsb.main import app


@patch("kbsb.club.api_club.validate_membertoken")
@patch("kbsb.club.api_club.verify_club_access")
def test_verify_club_access(
    verify_club_access: AsyncMock,
    vmt: MagicMock,
):
    client = TestClient(app)
    vmt.return_value = 123
    verify_club_access.return_value = True
    resp = client.get("/api/v1/clubs/clb/club/699/access/CLubAdmin,InterclubAdmin")
    assert resp.status_code == 200
    assert resp.json() == True
