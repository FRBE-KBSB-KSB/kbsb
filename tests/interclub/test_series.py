import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from freezegun import freeze_time
from datetime import date

from kbsb.interclubs import GAMERESULT, ICSeriesDB
from kbsb.interclubs.series import (
    mgmt_saveICresults,
    clb_saveICresults,
    calc_points,
    isRoundOpen,
)


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@pytest.mark.asyncio
async def test_mgmt_saveICresults(
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="", overruled=None)
    # encounters against club 0 (bye) are skipped, so use real clubs
    encounter1 = ic_encounter_factory.build(
        games=[game1], icclub_home=101, icclub_visit=201
    )
    round1 = ic_round_factory.build(encounters=[encounter1])
    # the database returns an ICSeriesDB (mgmt_saveICresults asserts it)
    series1 = ICSeriesDB(
        id="series1", **ic_series_factory.build(rounds=[round1]).model_dump()
    )
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.result = "1-0"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await mgmt_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] is None


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@pytest.mark.asyncio
async def test_mgmt_saveICresults_overrule(
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    # encounters against club 0 (bye) are skipped, so use real clubs
    encounter1 = ic_encounter_factory.build(
        games=[game1], icclub_home=101, icclub_visit=201
    )
    round1 = ic_round_factory.build(encounters=[encounter1])
    # the database returns an ICSeriesDB (mgmt_saveICresults asserts it)
    series1 = ICSeriesDB(
        id="series1", **ic_series_factory.build(rounds=[round1]).model_dump()
    )
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.overruled = "0-1"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await mgmt_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] == "0-1"


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
# the results window is checked against the real date; keep it open
@patch("kbsb.interclubs.series.check_results_open")
@pytest.mark.asyncio
async def test_clb_saveICresults(
    check_results_open: AsyncMock,
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="", overruled=None)
    # encounters against club 0 (bye) are skipped, so use real clubs
    encounter1 = ic_encounter_factory.build(
        games=[game1], icclub_home=101, icclub_visit=201
    )
    round1 = ic_round_factory.build(encounters=[encounter1])
    # the database returns an ICSeriesDB (clb_saveICresults asserts it)
    series1 = ICSeriesDB(
        id="series1", **ic_series_factory.build(rounds=[round1]).model_dump()
    )
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.result = "1-0"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await clb_saveICresults([resultitem1])
    check_results_open.assert_awaited_once()
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    # the stored game gets the model default, not None
    assert game["overruled"] == GAMERESULT.NOTOVERRULED


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@patch("kbsb.interclubs.series.check_results_open")
@pytest.mark.asyncio
async def test_clb_saveICresults_overrule(
    check_results_open: AsyncMock,
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    # a club cannot overrule a result: the overruled value it sends is dropped
    game1 = ic_game_factory.build(
        result="1-0", overruled=None, idnumber_home=1, idnumber_visit=2
    )
    encounter1 = ic_encounter_factory.build(
        games=[game1], icclub_home=101, icclub_visit=201
    )
    round1 = ic_round_factory.build(encounters=[encounter1])
    series1 = ICSeriesDB(
        id="series1", **ic_series_factory.build(rounds=[round1]).model_dump()
    )
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.overruled = "0-1"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await clb_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] == GAMERESULT.NOTOVERRULED


def test_calc_points(ic_encounter_factory, ic_game_factory):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    game2 = ic_game_factory.build(result="½-½", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1, game2], played=False)
    calc_points(encounter1)
    assert encounter1.played
    assert encounter1.boardpoint2_home == 3
    assert encounter1.boardpoint2_visit == 1
    assert encounter1.matchpoint_home == 2
    assert encounter1.matchpoint_visit == 0


def test_calc_points_empty(ic_encounter_factory, ic_game_factory):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    game2 = ic_game_factory.build(result="", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1, game2], played=False)
    calc_points(encounter1)
    assert not encounter1.played
    assert encounter1.boardpoint2_home == 2
    assert encounter1.boardpoint2_visit == 0
    assert encounter1.matchpoint_home == 0
    assert encounter1.matchpoint_visit == 0


def test_calc_points_overrule(ic_encounter_factory, ic_game_factory):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    game2 = ic_game_factory.build(result="½-½", overruled="0-1")
    encounter1 = ic_encounter_factory.build(games=[game1, game2], played=False)
    calc_points(encounter1)
    assert encounter1.played
    assert encounter1.boardpoint2_home == 2
    assert encounter1.boardpoint2_visit == 2
    assert encounter1.matchpoint_home == 1
    assert encounter1.matchpoint_visit == 1


@patch("kbsb.interclubs.series.load_icdata")
@pytest.mark.asyncio
async def test_isRoundOpen(load_icdata: AsyncMock):
    # a round opens at 14:00 Europe/Brussels (13:00 UTC in winter) on its
    # date; division 6 plays the 9-round calendar, the others the 11-round one
    load_icdata.return_value = {
        "rounds11": {1: date(2020, 1, 3)},
        "rounds9": {1: date(2020, 1, 4)},
    }
    with freeze_time("2020-01-03 12:50:00"):
        assert not await isRoundOpen(1)
    with freeze_time("2020-01-03 13:10:00"):
        assert await isRoundOpen(1)
        assert not await isRoundOpen(2)
        assert not await isRoundOpen(1, 6)
    with freeze_time("2020-01-04 13:10:00"):
        assert await isRoundOpen(1, 6)


# signing and overwriting


def _setup_signing(
    dbSeries,
    dbStandings,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
    **enc_fields,
):
    game1 = ic_game_factory.build(
        result="1-0", overruled=None, idnumber_home=1, idnumber_visit=2
    )
    encounter1 = ic_encounter_factory.build(
        games=[game1], icclub_home=101, icclub_visit=201, played=True, **enc_fields
    )
    round1 = ic_round_factory.build(encounters=[encounter1])
    series1 = ICSeriesDB(
        id="series1", **ic_series_factory.build(rounds=[round1]).model_dump()
    )
    dbSeries.find_single = AsyncMock(return_value=series1)
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    return game1, encounter1, round1


def _item(ic_result_item_factory, encounter1, round1, games, **fields):
    return ic_result_item_factory.build(
        games=games,
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
        **fields,
    )


def _stored_encounter(dbSeries):
    return dbSeries.update.call_args[0][1]["rounds"][0]["encounters"][0]


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@patch("kbsb.interclubs.series.check_results_open")
@pytest.mark.asyncio
async def test_clb_overwrite_removes_signatures(
    check_results_open,
    dbSeries,
    dbStandings,
    calc_points,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    # the visiting club signed 1-0; the home club changes it to a draw
    game1, encounter1, round1 = _setup_signing(
        dbSeries,
        dbStandings,
        ic_series_factory,
        ic_game_factory,
        ic_encounter_factory,
        ic_round_factory,
        ic_standings_db_factory,
        signhome_idnumber=0,
        signvisit_idnumber=222,
    )
    changed = game1.model_copy()
    changed.result = "½-½"
    item = _item(
        ic_result_item_factory,
        encounter1,
        round1,
        [changed],
        signhome_idnumber=0,
        signvisit_idnumber=222,
    )
    await clb_saveICresults([item], frozenset({101}))
    enc = _stored_encounter(dbSeries)
    assert enc["games"][0]["result"] == "½-½"
    assert enc["signhome_idnumber"] == 0
    assert enc["signvisit_idnumber"] == 0
    assert enc["signvisit_ts"] is None


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@patch("kbsb.interclubs.series.check_results_open")
@pytest.mark.asyncio
async def test_clb_sign_stale_card_refused(
    check_results_open,
    dbSeries,
    dbStandings,
    calc_points,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    # the stored result is 1-0; the visiting club signs a card still showing
    # an older 0-1: refused, nothing stored
    from reddevil.core import RdBadRequest

    game1, encounter1, round1 = _setup_signing(
        dbSeries,
        dbStandings,
        ic_series_factory,
        ic_game_factory,
        ic_encounter_factory,
        ic_round_factory,
        ic_standings_db_factory,
        signhome_idnumber=0,
        signvisit_idnumber=0,
    )
    stale = game1.model_copy()
    stale.result = "0-1"
    item = _item(
        ic_result_item_factory,
        encounter1,
        round1,
        [stale],
        signhome_idnumber=0,
        signvisit_idnumber=222,
    )
    with pytest.raises(RdBadRequest) as e:
        await clb_saveICresults([item], frozenset({201}))
    assert e.value.description == "ResultChangedReload"
    dbSeries.update.assert_not_awaited()


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@patch("kbsb.interclubs.series.check_results_open")
@pytest.mark.asyncio
async def test_clb_sign_current_card(
    check_results_open,
    dbSeries,
    dbStandings,
    calc_points,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    # signing the card as stored, padded with an empty board, keeps the home
    # signature and adds the visiting one
    game1, encounter1, round1 = _setup_signing(
        dbSeries,
        dbStandings,
        ic_series_factory,
        ic_game_factory,
        ic_encounter_factory,
        ic_round_factory,
        ic_standings_db_factory,
        signhome_idnumber=111,
        signvisit_idnumber=0,
    )
    empty = ic_game_factory.build(
        result="", overruled=None, idnumber_home=None, idnumber_visit=None
    )
    item = _item(
        ic_result_item_factory,
        encounter1,
        round1,
        [game1.model_copy(), empty],
        signhome_idnumber=111,
        signvisit_idnumber=222,
    )
    await clb_saveICresults([item], frozenset({201}))
    enc = _stored_encounter(dbSeries)
    assert enc["signhome_idnumber"] == 111
    assert enc["signvisit_idnumber"] == 222
    assert enc["signvisit_ts"] is not None


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@patch("kbsb.interclubs.series.check_results_open")
@pytest.mark.asyncio
async def test_clb_overwrite_keeps_overrule(
    check_results_open,
    dbSeries,
    dbStandings,
    calc_points,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    # a club save keeps the tournament director's overrule on that board
    game1, encounter1, round1 = _setup_signing(
        dbSeries,
        dbStandings,
        ic_series_factory,
        ic_game_factory,
        ic_encounter_factory,
        ic_round_factory,
        ic_standings_db_factory,
    )
    series1 = dbSeries.find_single.return_value
    series1.rounds[0].encounters[0].games[0].overruled = "0-1 FF"
    sent = game1.model_copy()
    sent.overruled = None
    item = _item(ic_result_item_factory, encounter1, round1, [sent])
    await clb_saveICresults([item], frozenset({101}))
    assert _stored_encounter(dbSeries)["games"][0]["overruled"] == "0-1 FF"
