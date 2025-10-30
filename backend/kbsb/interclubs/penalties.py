# copyright Ruben Decrop 2012 - 2022

import logging
import asyncio
from io import StringIO, BytesIO
from csv import DictWriter
from reddevil.filestore.filestore import (
    list_bucket_files,
    read_bucket_content,
    write_bucket_content,
)
from reddevil.core import RdInternalServerError
from .validation import LineUpValidation
from .icclubs import anon_getICclubs
from .md_interclubs import (
    ICTeam,
)

logger = logging.getLogger(__name__)
icdata = None

# we are caching the series data per round

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
    lineUpValidation = LineUpValidation()
    icclubs = await anon_getICclubs()
    for icclub in icclubs:
        logger.info(f"write penalties for club {icclub.idclub} round {round}")
        await lineUpValidation.validate_results(icclub.idclub, round)
    logger.info(f"validationerrors: {len(lineUpValidation.validationerrors)}")
    f = StringIO()
    writer = DictWriter(
        f,
        fieldnames=[
            "division",
            "index",
            "round",
            "icclub_offender",
            "name",
            "pnr_offender",
            "errormessage",
            "icclub_opponent",
            "name_opponent",
            "boardnr",
        ],
    )
    writer.writeheader()
    writer.writerows((rec.dict() for rec in lineUpValidation.validationerrors))
    report = f.getvalue()
    logger.debug(f"report: {len(report)}")
    try:
        write_bucket_content(
            f"icn/penalties_R{round}.csv", BytesIO(report.encode("utf-8"))
        )
        logger.info(f"icn/penalties_R{round}.csv report created")
    except Exception as e:
        logger.info(f"failed to write FIDE file icn/penalties_R{round}.csv")
        logger.exception(e)
        raise RdInternalServerError("Failed to write penalties report")


async def list_penalties_reports() -> list[str]:
    """
    endpoint to list the penalties reports in the cloud
    """
    ...
    try:
        files = list_bucket_files("icn")
    except Exception as e:
        logger.info("failed to list penalties reports")
        logger.exception(e)
        return []
    await asyncio.sleep(0)
    return [f.split("/")[1] for f in files if f.startswith("icn/penalties")]


async def get_penalties_report(path: str) -> str:
    """
    get the content of a penalties report
    """
    ...
    try:
        report = read_bucket_content(f"icn/{path}")
    except Exception as e:
        logger.info("failed to list penalties reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return report
