# copyright Ruben Decrop 2012 - 2022

import logging
import asyncio

from datetime import datetime, timezone, timedelta, time
from csv import DictWriter
from io import StringIO, BytesIO
from reddevil.core import RdInternalServerError
from reddevil.filestore.filestore import (
    write_bucket_content,
    read_bucket_content,
    list_bucket_files,
)
from .md_interclubs import (
    DbICSeries,
    ICSeries,
    DbICClub,
    ICClubDB,
    ICRound,
    ICTeam,
)
from .helpers import load_icdata
from .validation import LineUpValidation

logger = logging.getLogger(__name__)
icdata = None

# we are caching the series data per round
allseries = {}

issues = []
playerratings = {}
fideratings = {}
playertitular = {}
allclubs = []
doublepairings = [
    # (401, 4, "E", 1, 12),
    # (401, 4, "F", 6, 7),
    # (401, 5, "H", 1, 2),
    # (401, 5, "M", 8, 9),
    # (230, 5, "A", 3, 10),
    # (230, 5, "O", 6, 7),
    # (607, 4, "H", 1, 12),
    # (601, 4, "H", 6, 7),
    # (601, 5, "J", 6, 7),
    # (548, 5, "J", 1, 3),
    # (436, 5, "Q", 1, 10),
    # (703, 5, "B", 1, 5),
]


async def write_penalties_report(round: int):
    """
    endpoint to write a penalties report
    """
    ...
    # global icdata
    # logger.debug(f"writing penalties report for round {round}")
    # icdata = await load_icdata()
    # await read_interclubseries()
    # await read_interclubratings()
    # check_round(round)
    # f = StringIO()
    # writer = DictWriter(
    #     f,
    #     fieldnames=[
    #         "reason",
    #         "division",
    #         "pairingnr",
    #         "boardnumber",
    #         "guilty",
    #         "opponent",
    #     ],
    # )
    # writer.writeheader()
    # writer.writerows(issues)
    # report = f.getvalue()
    # logger.debug(f"report: {len(report)}")
    # try:
    #     write_bucket_content(
    #         f"icn/penalties_R{round}.txt", BytesIO(report.encode("utf-8"))
    #     )
    #     logger.info(f"icn/penalties_R{round}.csv report created")
    # except Exception as e:
    #     logger.info(f"failed to write FIDE file icn/penalties_R{round}.csv")
    #     logger.exception(e)
    #     raise RdInternalServerError("Failed to write penalties report")


async def list_penalties_reports() -> list[str]:
    """
    endpoint to list the penalties reports in the cloud
    """
    ...
    # try:
    #     files = list_bucket_files("icn")
    # except Exception as e:
    #     logger.info("failed to list penalties reports")
    #     logger.exception(e)
    # await asyncio.sleep(0)
    # return [f.split("/")[1] for f in files if f.startswith("icn/penalties")]


async def get_penalties_report(path: str) -> str:
    """
    get the content of a penalties report
    """
    ...
    # try:
    #     report = read_bucket_content(f"icn/{path}")
    # except Exception as e:
    #     logger.info("failed to list penalties reports")
    #     logger.exception(e)
    # await asyncio.sleep(0)
    # return report


def getteam(clb, teamname) -> ICTeam:
    ...
    # for t in clb.teams:
    #     if t.name == teamname:
    #         return t
    # logger.info(f"We're fucked to get team {teamname}")


async def read_interclubseries(round: int):
    ...
    # logger.info("reading interclub results")
    # for s in await DbICSeries.find_multiple({"_model": ICSeries}):
    #     allseries[(s.division, s.index)] = s


def check_round(r):
    ...
    # global issues
    # issues = []
    # logger.info("checking forfaits")
    # check_forfaits(r)
    # logger.info("checking signatures")
    # check_signatures(r)
    # logger.info("checking player order")
    # check_order_players(r)
    # logger.info("checking average")
    # check_average_elo(r)
    # logger.info("checking titular")
    # check_titular_ok(r)
    # logger.info("checking reserves in single series")
    # check_reserves_in_single_series(r)
    # logger.info("checking reserves elo too high")
    # check_reserves_elotoohigh(r)
    # logger.info("done")
