import pytest


@pytest.fixture
def playerlist101(ic_player_factory):
    return {
        10101: ic_player_factory.build(
            idnumber=10101, name="Player 1", assignedrating=1510, titular="T101 2"
        ),
        10102: ic_player_factory.build(
            idnumber=10102, name="Player 2", assignedrating=1520, titular="T101 2"
        ),
        10103: ic_player_factory.build(
            idnumber=10103, name="Player 3", assignedrating=1530, titular="T101 2"
        ),
        10104: ic_player_factory.build(
            idnumber=10104, name="Player 4", assignedrating=1540, titular="T101 2"
        ),
        10105: ic_player_factory.build(
            idnumber=10105, name="Player 5", assignedrating=1550, titular="T101 2"
        ),
        10106: ic_player_factory.build(
            idnumber=10106, name="Player 6", assignedrating=1560, titular="T101 2"
        ),
        10107: ic_player_factory.build(
            idnumber=10107, name="Player 7", assignedrating=1570, titular="T101 2"
        ),
        10108: ic_player_factory.build(
            idnumber=10108, name="Player 8", assignedrating=1580, titular="T101 2"
        ),
        10109: ic_player_factory.build(
            idnumber=10109, name="Player 9", assignedrating=1590, titular="T101 2"
        ),
        10110: ic_player_factory.build(
            idnumber=10110, name="Player 10", assignedrating=1600, titular="T101 1"
        ),
        10111: ic_player_factory.build(
            idnumber=10111, name="Player 11", assignedrating=1610, titular="T101 1"
        ),
        10112: ic_player_factory.build(
            idnumber=10112, name="Player 12", assignedrating=1620, titular="T101 1"
        ),
        10113: ic_player_factory.build(
            idnumber=10113, name="Player 13", assignedrating=1630, titular="T101 1"
        ),
        10114: ic_player_factory.build(
            idnumber=10114, name="Player 14", assignedrating=1640, titular="T101 1"
        ),
        10115: ic_player_factory.build(
            idnumber=10115, name="Player 15", assignedrating=1650, titular="T101 1"
        ),
        10116: ic_player_factory.build(
            idnumber=10116, name="Player 16", assignedrating=1660, titular="T101 1"
        ),
        10120: ic_player_factory.build(
            idnumber=10120, name="Player 20", assignedrating=1400, titular=None
        ),
        10121: ic_player_factory.build(
            idnumber=10121, name="Player 21", assignedrating=1410, titular=None
        ),
        10122: ic_player_factory.build(
            idnumber=10122, name="Player 22", assignedrating=1420, titular=None
        ),
        10123: ic_player_factory.build(
            idnumber=10123, name="Player 23", assignedrating=1430, titular=None
        ),
        10124: ic_player_factory.build(
            idnumber=10124, name="Player 24", assignedrating=1440, titular=None
        ),
        10125: ic_player_factory.build(
            idnumber=10125, name="Player 25", assignedrating=1450, titular=None
        ),
    }


@pytest.fixture
def playerlist201(ic_player_factory):
    return {
        20101: ic_player_factory.build(
            idnumber=20101, name="Speler 1", assignedrating=1515, titular="T201 2"
        ),
        20102: ic_player_factory.build(
            idnumber=20102, name="Speler 2", assignedrating=1525, titular="T201 2"
        ),
        20103: ic_player_factory.build(
            idnumber=20103, name="Speler 3", assignedrating=1535, titular="T201 2"
        ),
        20104: ic_player_factory.build(
            idnumber=20104, name="Speler 4", assignedrating=1545, titular="T201 2"
        ),
        20105: ic_player_factory.build(
            idnumber=20105, name="Speler 5", assignedrating=1555, titular="T201 2"
        ),
        20106: ic_player_factory.build(
            idnumber=20106, name="Speler 6", assignedrating=1565, titular="T201 2"
        ),
        20107: ic_player_factory.build(
            idnumber=20107, name="Speler 7", assignedrating=1575, titular="T201 2"
        ),
        20108: ic_player_factory.build(
            idnumber=20108, name="Speler 8", assignedrating=1585, titular="T201 2"
        ),
        20109: ic_player_factory.build(
            idnumber=20109, name="Speler 9", assignedrating=1595, titular="T201 1"
        ),
        20110: ic_player_factory.build(
            idnumber=20110, name="Speler 10", assignedrating=1605, titular="T201 1"
        ),
        20111: ic_player_factory.build(
            idnumber=20111, name="Speler 11", assignedrating=1615, titular="T201 1"
        ),
        20112: ic_player_factory.build(
            idnumber=20112, name="Speler 12", assignedrating=1625, titular="T201 1"
        ),
        20113: ic_player_factory.build(
            idnumber=20113, name="Speler 13", assignedrating=1635, titular="T201 1"
        ),
        20114: ic_player_factory.build(
            idnumber=20114, name="Speler 14", assignedrating=1645, titular="T201 1"
        ),
        20115: ic_player_factory.build(
            idnumber=20115, name="Speler 15", assignedrating=1655, titular="T201 1"
        ),
        20116: ic_player_factory.build(
            idnumber=20116, name="Speler 16", assignedrating=1665, titular="T201 1"
        ),
        20120: ic_player_factory.build(
            idnumber=20120, name="Speler 20", assignedrating=1405, titular=None
        ),
        20121: ic_player_factory.build(
            idnumber=20121, name="Speler 21", assignedrating=1415, titular=None
        ),
        20122: ic_player_factory.build(
            idnumber=20122, name="Speler 22", assignedrating=1425, titular=None
        ),
        20123: ic_player_factory.build(
            idnumber=20123, name="Speler 23", assignedrating=1435, titular=None
        ),
        20124: ic_player_factory.build(
            idnumber=20124, name="Speler 24", assignedrating=1445, titular=None
        ),
        20125: ic_player_factory.build(
            idnumber=20125, name="Speler 25", assignedrating=1455, titular=None
        ),
    }


@pytest.fixture
def team101_1(ic_team_factory):
    return ic_team_factory.build(
        idclub=101,
        division=0,
        index="",
        name="Team101 1",
        pairingnumber=1,
    )


@pytest.fixture
def team101_2(ic_team_factory):
    return ic_team_factory.build(
        idclub=101,
        division=0,
        index="",
        name="Team101 2",
        pairingnumber=1,
    )


@pytest.fixture
def encounter101_201(ic_encounter_factory):
    return ic_encounter_factory.build(
        icclub_home=101,
        icclub_visit=201,
        games=[],
        pairingnumber_home=1,
        pairingnumber_visit=12,
    )


@pytest.fixture
def round4(ic_round_factory, encounter101_201):
    return ic_round_factory.build(
        encounters=[encounter101_201],
        round=4,
    )


@pytest.fixture
def series5A(ic_series_factory, team101_1, round4):
    team101_1.division = 5
    team101_1.index = "A"
    return ic_series_factory.build(
        rounds=[round4],
        teams=[team101_1],
        division=5,
        index="A",
    )


@pytest.fixture
def series4A(ic_series_factory, team101_1, round4):
    team101_1.division = 4
    team101_1.index = "A"
    return ic_series_factory.build(
        rounds=[round4],
        teams=[team101_1],
        division=4,
        index="A",
    )


@pytest.fixture
def series3A(ic_series_factory, team101_1, round4):
    team101_1.division = 3
    team101_1.index = "A"
    return ic_series_factory.build(
        rounds=[round4],
        teams=[team101_1],
        division=3,
        index="A",
    )


@pytest.fixture
def series2A(ic_series_factory, team101_1, round4):
    team101_1.division = 2
    team101_1.index = "A"
    return ic_series_factory.build(
        rounds=[round4],
        teams=[team101_1],
        division=2,
        index="A",
    )


@pytest.fixture
def series1(ic_series_factory, team101_1, round4):
    team101_1.division = 1
    team101_1.index = ""
    return ic_series_factory.build(
        rounds=[round4],
        teams=[team101_1],
        division=1,
        index="",
    )
