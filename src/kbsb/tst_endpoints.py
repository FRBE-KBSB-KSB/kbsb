# This file creates some test endpoints
# the endpoints are excluded from the api docs  (endpoint /docs)

import logging

from kbsb.main import app

logger = logging.getLogger(__name__)


# this endpoint is useful to test if the server is running and accepting http requests
@app.get("/api/hello", include_in_schema=False)
def api_hello():
    logger.info("calling hello endpoint")
    return "hello world"
