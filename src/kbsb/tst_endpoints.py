# This file creates some test endpoints
# the endpoints are excluded from the api docs  (endpoint /docs)

import logging

from fastapi.responses import StreamingResponse
from kbsb import ROOT_DIR
from kbsb.main import app

logger = logging.getLogger(__name__)


# this endpoint is useful to test if the server is running and accepting http requests
@app.get("/api/test/hello", include_in_schema=False)
def api_hello():
    logger.info("calling hello endpoint")
    return "hello world"


@app.get("/api/test/excel", include_in_schema=False)
def api_excel():
    logger.info(f"calling excel endpoint {ROOT_DIR}")
    excpath = ROOT_DIR / "src" / "kbsb" / "templates" / "test" / "test.xlsx"
    with open(excpath, "rb") as f:
        buf = f.read()
    headers = {"Content-Disposition": 'attachment; filename="test.xlsx"'}
    return StreamingResponse(
        iter([buf]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


# @app.get("/api/test/mail", include_in_schema=False)
# def hello():
#     test_mail()
#     return "Mail sent"


# @app.get("/api/test/penalties", include_in_schema=False)
# async def penalties():
#     await write_penalties_report(1)
#     return "done"
