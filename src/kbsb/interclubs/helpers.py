import logging
from collections.abc import Iterable
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import yaml
from reddevil.core import RdBadRequest, RdInternalServerError, get_settings
from reddevil.filestore.filestore import get_file

from kbsb import ROOT_DIR

from .md_interclubs import (
    DbICClub,
    ICClubDB,
)

logger = logging.getLogger(__name__)


async def load_icdata():
    icdata = getattr(load_icdata, "icdata", None)
    if not icdata:
        settings = get_settings()
        if settings.ICDATA == "cloud":
            icdr = await get_file("data", "ic2627.yml")
            icdata = yaml.load(icdr.body, Loader=yaml.SafeLoader)
            logger.info("loaded icdata from cloud")
        if settings.ICDATA == "local":
            icdata_path = ROOT_DIR / "shared" / "cloud" / "data" / "ic2627.yml"
            icdata = yaml.load(icdata_path.read_text(), Loader=yaml.SafeLoader)
            logger.info("loaded icdata from local")
        load_icdata.icdata = icdata
    return icdata


# season windows of the club routes
# The site checks these in the browser (components/interclubs/*.vue and
# pages/tools/interclub_protected.vue). The server repeats them with the same
# times and boundaries, so a club can do no more over the API than on the
# site. The /mgmt routes never call them.

belzone = ZoneInfo("Europe/Brussels")


def _asdate(d: date | str) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d)[0:10])


def _sitedate(d: date | str) -> datetime:
    """
    a season date as the site reads it: new Date("YYYY-MM-DD") is midnight
    UTC, a date with a time is local (Brussels) time
    """
    if isinstance(d, str) and len(d) > 10:
        d = datetime.fromisoformat(d)
    if isinstance(d, datetime):
        return d if d.tzinfo else d.replace(tzinfo=belzone)
    return datetime.combine(_asdate(d), time(0), tzinfo=UTC)


def _roundtime(icdata: dict, calendar: str, round: int, hour: int) -> datetime | None:
    """
    a round date at the given hour, as the site reads it with
    new Date("YYYY-MM-DDThh:00"): local (Brussels) time
    """
    d = (icdata.get(calendar) or {}).get(round)
    if not d:
        return None
    return datetime.combine(_asdate(d), time(hour), tzinfo=belzone)


def _calendars(division: int) -> list[str]:
    """
    the site takes the round date from rounds11 for every division (IB-10);
    division 6 plays the rounds9 calendar, so its own dates count as well
    """
    return ["rounds11", "rounds9"] if division == 6 else ["rounds11"]


def planning_open(icdata: dict, round: int, division: int, now: datetime) -> bool:
    """
    Planning.vue: the line-up of a round can change until 14:00 on its day
    """
    for cal in _calendars(division):
        expiry = _roundtime(icdata, cal, round, 14)
        if expiry and now <= expiry:
            return True
    return False


def results_open(icdata: dict, round: int, division: int, now: datetime) -> bool:
    """
    Results.vue: the results of a round can be entered from 15:00 on its day
    during 33 hours (counted in real hours, as the site does)
    """
    for cal in _calendars(division):
        opened = _roundtime(icdata, cal, round, 15)
        if opened:
            opened = opened.astimezone(UTC)
            if opened <= now <= opened + timedelta(hours=33):
                return True
    return False


def playerlist_open(icdata: dict, now: datetime) -> bool:
    """
    Playerlist.vue: the player list can change strictly inside one of the
    periods of playerlist_data
    """
    for p in icdata.get("playerlist_data") or []:
        if _sitedate(p["start"]) < now < _sitedate(p["end"]):
            return True
    return False


def registration_open(icdata: dict, now: datetime) -> bool:
    """
    interclub_protected.vue: the registration can change from the start up to
    the end of registration_data, both included
    """
    rd = icdata.get("registration_data") or {}
    if not rd.get("start") or not rd.get("end"):
        return False
    return _sitedate(rd["start"]) <= now <= _sitedate(rd["end"])


async def check_planning_open(
    round: int, divisions: Iterable[int], now: datetime | None = None
) -> None:
    """
    raise PlanningClosed unless the planning of the round is open for all
    the divisions
    """
    icdata = await load_icdata()
    now = now or datetime.now(UTC)
    for division in set(divisions) or {0}:
        if not planning_open(icdata, round, division, now):
            raise RdBadRequest(description="PlanningClosed")


async def check_results_open(
    rounds: Iterable[tuple[int, int]], now: datetime | None = None
) -> None:
    """
    raise ResultsClosed unless the result entry is open for every
    (round, division)
    """
    icdata = await load_icdata()
    now = now or datetime.now(UTC)
    for round, division in rounds:
        if not results_open(icdata, round, division, now):
            raise RdBadRequest(description="ResultsClosed")


async def check_playerlist_open(now: datetime | None = None) -> None:
    """
    raise PlayerlistClosed outside the player list periods
    """
    icdata = await load_icdata()
    if not playerlist_open(icdata, now or datetime.now(UTC)):
        raise RdBadRequest(description="PlayerlistClosed")


async def check_registration_open(now: datetime | None = None) -> None:
    """
    raise RegistrationClosed outside the registration window
    """
    icdata = await load_icdata()
    if not registration_open(icdata, now or datetime.now(UTC)):
        raise RdBadRequest(description="RegistrationClosed")


async def load_all_icclubs():
    playerratings = getattr(load_all_icclubs, "playerratings", None)
    clubs = getattr(load_all_icclubs, "clubs", None)
    titulars = getattr(load_all_icclubs, "titulars", None)
    fideratings = getattr(load_all_icclubs, "fideratings", None)
    if not playerratings:
        logger.info("reading interclub ratings")
        playerratings = {}
        clubs = []
        titulars = {}
        fideratings = {}
        for clb in await DbICClub.find_multiple(
            {"_model": ICClubDB, "registered": True}
        ):
            clubs.append(clb)
            for p in clb.players:
                if p.nature in ["assigned", "imported"]:
                    playerratings[p.idnumber] = p.assignedrating
                    fideratings[p.idnumber] = p.fiderating
                    if p.titular:
                        teamix = int(p.titular.split(" ")[-1])
                        for t in clb.teams:
                            if t.name == p.titular:
                                break
                        else:
                            logger.error(
                                f"Team {p.titular} not found in club {clb.name}"
                            )
                            raise RdInternalServerError("Fucked")
                        titulars[p.idnumber] = {
                            "team": teamix,
                            "division": t.division,
                            "index": t.index,
                            "pairingnumber": t.pairingnumber,
                        }
            load_all_icclubs.playerratings = playerratings  # pyright: ignore[reportFunctionMemberAccess]
            load_all_icclubs.fideratings = fideratings  # pyright: ignore[reportFunctionMemberAccess]
            load_all_icclubs.clubs = clubs  # pyright: ignore[reportFunctionMemberAccess]
            load_all_icclubs.titulars = titulars  # pyright: ignore[reportFunctionMemberAccess]
    return (playerratings, clubs, titulars, fideratings)


ptable12 = (
    [(1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)],
    [(12, 7), (8, 6), (9, 5), (10, 4), (11, 3), (1, 2)],
    [(2, 12), (3, 1), (4, 11), (5, 10), (6, 9), (7, 8)],
    [(12, 8), (9, 7), (10, 6), (11, 5), (1, 4), (2, 3)],
    [(3, 12), (4, 2), (5, 1), (6, 11), (7, 10), (8, 9)],
    [(12, 9), (10, 8), (11, 7), (1, 6), (2, 5), (3, 4)],
    [(4, 12), (5, 3), (6, 2), (7, 1), (8, 11), (9, 10)],
    [(12, 10), (11, 9), (1, 8), (2, 7), (3, 6), (4, 5)],
    [(5, 12), (6, 4), (7, 3), (8, 2), (9, 1), (10, 11)],
    [(12, 11), (1, 10), (2, 9), (3, 8), (4, 7), (5, 6)],
    [(6, 12), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1)],
)

ptable10 = (
    [(1, 10), (2, 9), (3, 8), (4, 7), (5, 6)],
    [(10, 6), (7, 5), (8, 4), (9, 3), (1, 2)],
    [(2, 10), (3, 1), (4, 9), (5, 8), (6, 7)],
    [(10, 7), (8, 6), (9, 5), (1, 4), (2, 3)],
    [(3, 10), (4, 2), (5, 1), (6, 9), (7, 8)],
    [(10, 8), (9, 7), (1, 6), (2, 5), (3, 4)],
    [(4, 10), (5, 3), (6, 2), (7, 1), (8, 9)],
    [(10, 9), (1, 8), (2, 7), (3, 6), (4, 5)],
    [(5, 10), (6, 4), (7, 3), (8, 2), (9, 1)],
)
