import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from kbsb.club.club import (
    verify_club_access,
    ClubRoleNature,
)
from kbsb.core import RdForbidden


@patch("kbsb.club.club.get_club")
@pytest.mark.asyncio
async def test_verify_club_access_single(
    get_club: AsyncMock,
    club_factory,
    club_role_factory,
):
    club = club_factory.build()
    clubadmin = club_role_factory.build(
        nature=ClubRoleNature.ClubAdmin, memberlist=[12345]
    )
    get_club.return_value = club
    club.clubroles = [clubadmin]
    allowed = await verify_club_access(301, 12345, "ClubAdmin")
    assert allowed


@patch("kbsb.club.club.get_club")
@pytest.mark.asyncio
async def test_verify_club_access_dual(
    get_club: AsyncMock,
    club_factory,
    club_role_factory,
):
    club = club_factory.build()
    clubadmin = club_role_factory.build(
        nature=ClubRoleNature.ClubAdmin, memberlist=[12345]
    )
    get_club.return_value = club
    club.clubroles = [clubadmin]
    allowed = await verify_club_access(301, 12345, "ClubAdmin,InterclubAdmin")
    assert allowed


@patch("kbsb.club.club.get_club")
@pytest.mark.asyncio
async def test_verify_club_access_no(
    get_club: AsyncMock,
    club_factory,
    club_role_factory,
):
    club = club_factory.build()
    clubadmin = club_role_factory.build(
        nature=ClubRoleNature.ClubAdmin, memberlist=[12345]
    )
    get_club.return_value = club
    club.clubroles = [clubadmin]
    with pytest.raises(RdForbidden) as e:
        await verify_club_access(301, 54321, "ClubAdmin,InterclubAdmin")


# @patch("kbsb.interclubs.icclubs.find_icregistration")
# @pytest.mark.parametrize(
#     "assignedrating,fiderating,natrating",
#     [
#         (999, 0, 0),
#         (1500, 1800, 1601),
#         (1500, 1601, 1800),
#     ],
# )
# @pytest.mark.asyncio
# async def test_validate_players_elotoolow(
#     find_registration: AsyncMock,
#     assignedrating,
#     fiderating,
#     natrating,
#     ic_player_update_item_factory,
#     ic_enrollment_factory,
# ):
#     pl = ic_player_update_item_factory.build(
#         assignedrating=assignedrating,
#         fiderating=fiderating,
#         natrating=natrating,
#         nature="assigned",
#     )
#     pu = ICPlayerUpdate(players=[pl])
#     find_registration.return_value = ic_enrollment_factory.build(
#         teams1=0, teams2=0, teams3=0, teams4=0, teams5=1
#     )
#     errors = await clb_validateICPlayers(123, pu)
#     assert len(errors)
#     ve = errors[0]
#     assert ve.message == "Elo too low"
