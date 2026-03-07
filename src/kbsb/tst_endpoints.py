# This file creates some test endpoint
# the endpoints are excluded from the api docs  (endpoint /docs)

import logging

# from reddevil.core import get_settings
from kbsb.main import app
# from kbsb.core.mail import test_mail
# from kbsb.interclubs.penalties import write_penalties_report

logger = logging.getLogger(__name__)
# settings = get_settings()


# this endpoint is useful to test if the server is running and accepting http requests
@app.get("/api/hello", include_in_schema=False)
def api_hello():
    logger.info("calling hello endpoint")
    return "hello world"


# @app.get("/api/testmail", include_in_schema=False)
# def hello():
#     test_mail()
#     return "Mail sent"


# @app.get("/api/adhoc/penalties", include_in_schema=False)
# async def penalties():
#     await write_penalties_report(1)
#     return "done"
