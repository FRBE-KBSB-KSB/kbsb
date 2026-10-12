import pytest
import yaml

from kbsb import ROOT_DIR
from kbsb.interclubs.validation import LineUpValidation


@pytest.fixture()
def loaded_icdata():
    icdata_path = ROOT_DIR / "shared" / "cloud" / "data" / "ic2627.yml"
    return yaml.load(icdata_path.read_text(), Loader=yaml.SafeLoader)


@pytest.fixture
def encounter_541_511(ic_encounter_factory):
    return ic_encounter_factory.build(
        icclub_home=541,
        icclub_visit=511,
        games=[],
        pairingnumber_home=1,
        pairingnumber_visit=12,
    )


@pytest.fixture
def round1(ic_round_factory, encounter_541_511):
    return ic_round_factory.build(
        encounters=[encounter_541_511],
        round=1,
    )


@pytest.fixture
def playerlist_511(ic_player_factory):
    return {
        30523: ic_player_factory.build(
            idnumber=30523,
            name="Lecomte, Joakim",
            assignedrating=1574,
            fiderating=1574,
            titular="",
        ),
        30521: ic_player_factory.build(
            idnumber=30521,
            name="Lecomte, Maxim",
            assignedrating=1545,
            fiderating=1545,
            titular="",
        ),
        33477: ic_player_factory.build(
            idnumber=33477,
            name="Dequesne, Hugo",
            assignedrating=1010,
            fiderating=0,
            titular="",
        ),
        32899: ic_player_factory.build(
            idnumber=32899,
            name="Mezieres, Hugo",
            assignedrating=1015,
            fiderating=0,
            titular="",
        ),
    }


@pytest.fixture
def playerlist_541(ic_player_factory):
    return {
        30523: ic_player_factory.build(
            idnumber=30523,
            name="Lecomte, Joakim",
            assignedrating=1574,
            fiderating=1574,
            titular="",
        ),
        30521: ic_player_factory.build(
            idnumber=30521,
            name="Lecomte, Maxim",
            assignedrating=1545,
            fiderating=1545,
            titular="",
        ),
        33477: ic_player_factory.build(
            idnumber=33477,
            name="Dequesne, Hugo",
            assignedrating=1010,
            fiderating=0,
            titular="",
        ),
        32899: ic_player_factory.build(
            idnumber=32899,
            name="Mezieres, Hugo",
            assignedrating=1015,
            fiderating=0,
            titular="",
        ),
    }


@pytest.fixture
def team_511(ic_team_factory):
    return ic_team_factory.build(
        idclub=511,
        division=5,
        index="H",
        name="EDC 3",
        pairingnumber=12,
    )


@pytest.fixture
def team_541(ic_team_factory):
    return ic_team_factory.build(
        idclub=541,
        division=5,
        index="H",
        name="Leuze 5",
        pairingnumber=1,
    )


@pytest.fixture
def titulars_541(ic_player_factory):
    return {}


@pytest.fixture
def fideratings_541(ic_player_factory):
    return {
        30523: 1574,
        30521: 1545,
        33477: 0,
        32899: 0,
    }


@pytest.fixture
def fideratings_511(ic_player_factory):
    return {
        30523: 1574,
        30521: 1545,
        33477: 0,
        32899: 0,
    }


@pytest.fixture
def series5H(ic_series_factory, team_511, team_541, round1):
    return ic_series_factory.build(
        rounds=[round1],
        teams=[team_541, team_511],
        division=5,
        index="H",
    )


def test_5H_511_fiderating_too_high(
    series5H,
    playerlist_511,
    titulars_541,
    fideratings_541,
    ic_game_factory,
    loaded_icdata,
):

    lu = LineUpValidation()
    lu.seriesdict = {(5, "H"): series5H}
    lu.titulars = titulars_541
    lu.fideratings = fideratings_541
    lu.icdata = loaded_icdata
    players = [30523, 30521, 33477, 32899]
    opponents = [98919, 16531, 26464, 16858]
    games = [
        ic_game_factory.build(idnumber_home=opponents[i], idnumber_visit=players[i])
        for i in range(4)
    ]
    series5H.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist_511[ix].assignedrating for ix in players}
    lu.check_elo_limits(1, 511)
    assert not lu.validationerrors
