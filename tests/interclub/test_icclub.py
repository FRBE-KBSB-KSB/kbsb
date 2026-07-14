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
    ic_registration_factory,
):
    pl = ic_player_update_item_factory.build(
        assignedrating=assignedrating,
        fiderating=fiderating,
        natrating=natrating,
        nature="assigned",
    )
    pu = ICPlayerUpdate(players=[pl])
    find_registration.return_value = ic_registration_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1
    )
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Elo too low"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.parametrize(
    "nbtitulars",
    [4, 5, 6],
)
@pytest.mark.asyncio
async def test_validate_players_OK(
    find_registration: AsyncMock,
    nbtitulars,
    ic_player_update_item_factory,
    ic_registration_factory,
):
    pls = ic_player_update_item_factory.batch(
        nbtitulars,
        assignedrating=1500,
        fiderating=1500,
        natrating=1500,
        nature="assigned",
        titular="C 1",
    )
    for ix, pl in enumerate(pls):
        pl.assignedrating = pl.fiderating + ix
    pu = ICPlayerUpdate(players=pls)
    find_registration.return_value = ic_registration_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    errors = await clb_validateICPlayers(123, pu)
    assert not errors


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.parametrize(
    "assignedrating,fiderating,natrating",
    [
        (1801, 0, 0),
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
    ic_registration_factory,
):
    pls = ic_player_update_item_factory.batch(
        4,
        assignedrating=assignedrating,
        fiderating=fiderating,
        natrating=natrating,
        nature="assigned",
        titular="C 1",
    )
    for ix, pl in enumerate(pls):
        pl.assignedrating = pl.assignedrating + ix
    pu = ICPlayerUpdate(players=pls)
    find_registration.return_value = ic_registration_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    errors = await clb_validateICPlayers(123, pu)
    print("errors:", errors)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Elo too high"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.asyncio
async def test_validate_players_doubleelo(
    find_registration: AsyncMock,
    ic_player_update_item_factory,
    ic_registration_factory,
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
    find_registration.return_value = ic_registration_factory.build(
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
    ic_registration_factory,
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
    find_registration.return_value = ic_registration_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    pu = ICPlayerUpdate(players=pls)
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Too many titulars"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.asyncio
async def test_validate_players_titularnotenough(
    find_registration: AsyncMock,
    ic_player_update_item_factory,
    ic_registration_factory,
):
    pls = ic_player_update_item_factory.batch(
        3,
        fiderating=1500,
        natrating=1500,
        nature="assigned",
    )
    for ix, pl in enumerate(pls):
        pl.assignedrating = 1500 + ix
        pl.titular = "C 1"
    find_registration.return_value = ic_registration_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    pu = ICPlayerUpdate(players=pls)
    errors = await clb_validateICPlayers(123, pu)
    assert len(errors)
    ve = errors[0]
    assert ve.message == "Not enough titulars"


@patch("kbsb.interclubs.icclubs.find_icregistration")
@pytest.mark.asyncio
async def test_validate_players_titularok(
    find_registration: AsyncMock,
    ic_player_update_item_factory,
    ic_registration_factory,
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
    find_registration.return_value = ic_registration_factory.build(
        teams1=0, teams2=0, teams3=0, teams4=0, teams5=1, name="C"
    )
    pu = ICPlayerUpdate(players=pls)
    errors = await clb_validateICPlayers(123, pu)
    assert not errors
