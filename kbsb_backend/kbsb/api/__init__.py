# copyright Ruben Descrop 2015 - 2022
# copyright Chessdevil Consulting BVBA 2018 - 2022

import logging

log = logging.getLogger(__name__)


import reddevil.api.api_page
import reddevil.api.api_account
import kbsb.api.api_file
import kbsb.api.api_site
import kbsb.api.api_old

from kbsb.main import app
from pathlib import Path


@app.get("/api")
def root():
    return {"hello": "world"}


def walk(path):
    for p in Path(path).iterdir():
        if p.is_dir():
            yield from walk(p)
            continue
        yield p.resolve()


@app.get("/api/list")
def test():
    return list(walk("/etc/secrets"))


from fastapi.responses import Response


@app.get("/api/report")
def readme():
    from kbsb.service.file import readFilecontent

    contents = readFilecontent("reports_bm/20211122 PV OA - BO verslag__957163.pdf")
    return Response(contents, media_type="application/pdf")
