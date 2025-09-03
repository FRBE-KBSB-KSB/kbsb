import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from freezegun import freeze_time
from datetime import date

from kbsb.main import app
from kbsb.interclubs import ICGame
from kbsb.interclubs.validation import LineUpValidation
from tests.interclub.conftest import series5A


@pytest.mark.parametrize(
    "board,rating",
    [
        (1, 1545),
        (1, 1515),
        (2, 1545),
        (2, 1505),
        (3, 1545),
        (3, 1505),
        (4, 1535),
        (4, 1505),
    ],
)
def test_order_players_4_ok(
    board,
    rating,
    playerlist101,
    series5A,
    ic_game_factory,
):
    # Arrange
    lu = LineUpValidation()
    lu.series = {(5, "A"): series5A}
    players = [10104, 10103, 10102, 10101]
    opponents = [20104, 20103, 20102, 20101]
    games = [
        ic_game_factory.build(idnumber_home=players[i], idnumber_visit=opponents[i])
        for i in range(4)
    ]
    series5A.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist101[ix].assignedrating for ix in players}
    lu.playerratings[board - 1] = rating
    lu.check_order_players(4, 101)
    assert not lu.validationerrors


@pytest.mark.parametrize(
    "board,rating",
    [
        (1, 1505),
        (4, 1545),
    ],
)
def test_order_players_4_nok(
    board,
    rating,
    playerlist101,
    series5A,
    ic_game_factory,
):
    # Arrange
    lu = LineUpValidation()
    lu.series = {(5, "A"): series5A}
    players = [10104, 10103, 10102, 10101]
    opponents = [20104, 20103, 20102, 20101]
    games = [
        ic_game_factory.build(idnumber_home=players[i], idnumber_visit=opponents[i])
        for i in range(4)
    ]
    series5A.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist101[ix].assignedrating for ix in players}
    pix = players[board - 1]
    lu.playerratings[pix] = rating
    lu.check_order_players(4, 101)
    assert lu.validationerrors
    assert lu.validationerrors[0].errormessage == "home player order is not correct"


@pytest.mark.parametrize(
    "board,rating",
    [
        (1, 1565),
        (1, 1525),
        (2, 1565),
        (2, 1515),
        (3, 1565),
        (3, 1505),
        (4, 1565),
        (4, 1505),
        (5, 1555),
        (5, 1505),
        (6, 1545),
        (6, 1505),
    ],
)
def test_order_players_6_ok(
    board,
    rating,
    playerlist101,
    series3A,
    ic_game_factory,
):
    # Arrange
    lu = LineUpValidation()
    lu.series = {(3, "A"): series3A}
    players = [10106, 10105, 10104, 10103, 10102, 10101]
    opponents = [20106, 20105, 20104, 20103, 20102, 20101]
    games = [
        ic_game_factory.build(idnumber_home=players[i], idnumber_visit=opponents[i])
        for i in range(6)
    ]
    series3A.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist101[ix].assignedrating for ix in players}
    lu.playerratings[board - 1] = rating
    lu.check_order_players(4, 101)
    assert not lu.validationerrors


@pytest.mark.parametrize(
    "board,rating",
    [
        (1, 1515),
        (2, 1505),
        (5, 1565),
        (6, 1555),
    ],
)
def test_order_players_6_nok(
    board,
    rating,
    playerlist101,
    series3A,
    ic_game_factory,
):
    # Arrange
    lu = LineUpValidation()
    lu.series = {(3, "A"): series3A}
    players = [10106, 10105, 10104, 10103, 10102, 10101]
    opponents = [20106, 20105, 20104, 20103, 20102, 20101]
    games = [
        ic_game_factory.build(idnumber_home=players[i], idnumber_visit=opponents[i])
        for i in range(6)
    ]
    series3A.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist101[ix].assignedrating for ix in players}
    pix = players[board - 1]
    lu.playerratings[pix] = rating
    lu.check_order_players(4, 101)
    assert lu.validationerrors
    assert lu.validationerrors[0].errormessage == "home player order is not correct"


@pytest.mark.parametrize(
    "board,rating",
    [
        (1, 1585),
        (1, 1535),
        (2, 1585),
        (2, 1525),
        (3, 1585),
        (3, 1515),
        (4, 1585),
        (4, 1505),
        (5, 1585),
        (5, 1505),
        (6, 1575),
        (6, 1505),
        (7, 1565),
        (7, 1505),
        (8, 1555),
        (8, 1505),
    ],
)
def test_order_players_8_ok(
    board,
    rating,
    playerlist101,
    series2A,
    ic_game_factory,
):
    # Arrange
    lu = LineUpValidation()
    lu.series = {(2, "A"): series2A}
    players = [10108, 10107, 10106, 10105, 10104, 10103, 10102, 10101]
    opponents = [20108, 20107, 20106, 20105, 20104, 20103, 20102, 20101]
    games = [
        ic_game_factory.build(idnumber_home=players[i], idnumber_visit=opponents[i])
        for i in range(8)
    ]
    series2A.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist101[ix].assignedrating for ix in players}
    lu.playerratings[board - 1] = rating
    lu.check_order_players(4, 101)
    assert not lu.validationerrors


@pytest.mark.parametrize(
    "board,rating",
    [
        (1, 1525),
        (2, 1515),
        (3, 1505),
        (6, 1585),
        (7, 1575),
        (8, 1565),
    ],
)
def test_order_players_8_nok(
    board,
    rating,
    playerlist101,
    series2A,
    ic_game_factory,
):
    # Arrange
    lu = LineUpValidation()
    lu.series = {(2, "A"): series2A}
    players = [10108, 10107, 10106, 10105, 10104, 10103, 10102, 10101]
    opponents = [20108, 20107, 20106, 20105, 20104, 20103, 20102, 20101]
    games = [
        ic_game_factory.build(idnumber_home=players[i], idnumber_visit=opponents[i])
        for i in range(8)
    ]
    series2A.rounds[0].encounters[0].games = games
    lu.playerratings = {ix: playerlist101[ix].assignedrating for ix in players}
    pix = players[board - 1]
    lu.playerratings[pix] = rating
    lu.check_order_players(4, 101)
    assert lu.validationerrors
    assert lu.validationerrors[0].errormessage == "home player order is not correct"
