# copyright Chessdevil Consulting BVBA 2018 - 2020

# import reddevil.boardrole.api_brole
# import reddevil.boardmember.api_bmember
import reddevil.api.api_page
import reddevil.api.api_account
import reddevil.api.api_file

# import reddevil.api.api_boardrole
# import reddevil.api.api_boardmember

# import kbsb.api.api_member
# import kbsb.api.api_club
# import kbsb.api.api_book100

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
