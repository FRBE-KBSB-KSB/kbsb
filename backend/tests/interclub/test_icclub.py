import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from kbsb.interclubs.icclubs import (
    clb_validateICPlayers,
    create_icclub,
    get_icclub,
    ICClubDB,
    ICPlayerUpdate,
)


@patch("kbsb.interclubs.icclubs.DbICClub")
@pytest.mark.asyncio
async def test_create_icclub(
    DbICClub: MagicMock,
    ic_club_db_factory,
):
    icc = ic_club_db_factory.build()
    DbICClub.add = AsyncMock(return_value="123")
    id = await create_icclub(icc)
    assert id == "123"


@patch("kbsb.interclubs.icclubs.DbICClub")
@pytest.mark.asyncio
async def test_get_icclub(
    DbICClub: MagicMock,
    ic_club_db_factory,
):
    icc = ic_club_db_factory.build(idclub=17)
    DbICClub.find_single = AsyncMock(return_value=icc)
    c = await get_icclub({"idclub": 15})
    assert isinstance(c, ICClubDB)
    assert c.idclub == 17


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.parametrize(
    "assignedrating,fiderating,natrating",
    [
        (999, 0, 0),
        (1500, 1800, 1601),
        (1500, 1601, 1800),
    ],
)
@pytest.mark.asyncio
async def test_validate_players_elotoolow(
    find_registration: AsyncMock,
    assignedrating,
    fiderating,
    natrating,
    ic_player_update_item_factory,
    ic_enrollment_factory,
):
    pl = ic_player_update_item_factory.build(
        assignedrating=assignedrating,
        fiderating=fiderating,
        natrating=natrating,
        nature="assigned",
    )
    pu = ICPlayerUpdate(players=[pl])
    find_registration.return_value = ic_enrollment_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1
    )
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Elo too low"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.parametrize(
    "assignedrating,fiderating,natrating",
    [
        (1601, 0, 0),
        (1901, 1800, 1601),
        (1901, 1601, 1800),
    ],
)
@pytest.mark.asyncio
async def test_validate_players_elotoohigh(
    find_registration: AsyncMock,
    assignedrating,
    fiderating,
    natrating,
    ic_player_update_item_factory,
    ic_enrollment_factory,
):
    pl = ic_player_update_item_factory.build(
        assignedrating=assignedrating,
        fiderating=fiderating,
        natrating=natrating,
        nature="assigned",
    )
    pu = ICPlayerUpdate(players=[pl])
    find_registration.return_value = ic_enrollment_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1
    )
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Elo too high"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.parametrize(
    "assignedrating,fiderating,natrating",
    [(1600, 0, 0), (1000, 0, 0)],
)
@pytest.mark.asyncio
async def test_validate_players_elook(
    find_registration: AsyncMock,
    assignedrating,
    fiderating,
    natrating,
    ic_player_update_item_factory,
    ic_enrollment_factory,
):
    pl = ic_player_update_item_factory.build(
        assignedrating=assignedrating,
        fiderating=fiderating,
        natrating=natrating,
        nature="assigned",
    )
    pu = ICPlayerUpdate(players=[pl])
    find_registration.return_value = ic_enrollment_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1
    )
    errors = await clb_validateICPlayers(123, pu)
    assert not errors


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.asyncio
async def test_validate_players_doubleelo(
    find_registration: AsyncMock,
    ic_player_update_item_factory,
    ic_enrollment_factory,
):
    pl1 = ic_player_update_item_factory.build(
        assignedrating=1500,
        fiderating=1500,
        natrating=1500,
        nature="assigned",
    )
    pl2 = ic_player_update_item_factory.build(
        assignedrating=1500,
        fiderating=1501,
        natrating=1501,
        nature="assigned",
    )
    find_registration.return_value = ic_enrollment_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1
    )
    pu = ICPlayerUpdate(players=[pl1, pl2])
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Double ELO"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.asyncio
async def test_validate_players_titulartoomany(
    find_registration: AsyncMock,
    ic_player_update_item_factory,
    ic_enrollment_factory,
):
    pls = ic_player_update_item_factory.batch(
        7,
        fiderating=1500,
        natrating=1500,
        nature="assigned",
    )
    for ix, pl in enumerate(pls):
        pl.assignedrating = 1500 + ix
        pl.titular = "C 1"
    find_registration.return_value = ic_enrollment_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    pu = ICPlayerUpdate(players=pls)
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Too many titulars"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.asyncio
async def test_validate_players_titularok(
    find_registration: AsyncMock,
    ic_player_update_item_factory,
    ic_enrollment_factory,
):
    pls = ic_player_update_item_factory.batch(
        6,
        fiderating=1500,
        natrating=1500,
        nature="assigned",
    )
    for ix, pl in enumerate(pls):
        pl.assignedrating = 1500 + ix
        pl.titular = "C 1"
    find_registration.return_value = ic_enrollment_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    pu = ICPlayerUpdate(players=pls)
    errors = await clb_validateICPlayers(123, pu)
    assert not errors


# @patch("kbsb.interclubs.icclubs.DbICClub")
# @patch("kbsb.interclubs.icclubs.get_icclub")
# @patch("kbsb.interclubs.icclubs.find_icregistration")
# @patch("kbsb.interclubs.icclubs.update_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.sendEmail")
# @pytest.mark.asyncio
# async def test_set_interclubenrollment_existing(
#     sendEmail: MagicMock,
#     update_interclubenrollment: AsyncMock,
#     find_interclubenrollment: AsyncMock,
#     get_club_idclub: AsyncMock,
#     DbICEnrollment: MagicMock,
#     club_factory,
#     ic_enrollment_factory,
#     ic_enrollment_in_factory,
#     settings,
# ):
#     club1 = club_factory.build(idclub=123, federation="F")
#     enr1 = ic_enrollment_factory.build(idclub=123, id="id1")
#     enr2 = ic_enrollment_factory.build(idclub=123)
#     enr_in1 = ic_enrollment_in_factory.build()
#     get_club_idclub.return_value = club1
#     find_interclubenrollment.return_value = enr1
#     update_interclubenrollment.return_value = enr2
#     enr3 = await set_icregistration(456, enr_in1)
#     assert enr3 == enr2
#     sendEmail.assert_called()


# @patch("kbsb.interclubs.icclubs.DbICEnrollment2425")
# @patch("kbsb.interclubs.icclubs.get_club_idclub")
# @patch("kbsb.interclubs.icclubs.find_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.create_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.get_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.sendEmail")
# @pytest.mark.asyncio
# async def test_set_interclubenrollment_new(
#     sendEmail: MagicMock,
#     get_interclubenrollment: AsyncMock,
#     create_interclubenrollment: AsyncMock,
#     find_interclubenrollment: AsyncMock,
#     get_club_idclub: AsyncMock,
#     DbICEnrollment: MagicMock,
#     club_factory,
#     ic_enrollment_factory,
#     ic_enrollment_in_factory,
#     settings,
# ):
#     club1 = club_factory.build(idclub=123, federation="F")
#     enr2 = ic_enrollment_factory.build(idclub=123)
#     enr_in1 = ic_enrollment_in_factory.build()
#     get_club_idclub.return_value = club1
#     find_interclubenrollment.return_value = None
#     get_interclubenrollment.return_value = enr2
#     create_interclubenrollment.return_value = 123
#     enr3 = await set_icregistration(456, enr_in1)
#     assert enr3 == enr2
#     sendEmail.assert_called()
