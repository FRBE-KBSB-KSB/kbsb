from csv import DictReader
from pathlib import Path

import pytest_asyncio
from fastapi import FastAPI
from reddevil.core import (
    a_close_mongodb,
    a_connect_mongodb,
    a_get_mongodb,
    register_app,
)


@pytest_asyncio.fixture()
async def app():
    myapp = FastAPI()
    register_app(myapp, "tests.settings", "/api")
    a_connect_mongodb()
    db = a_get_mongodb()
    myapp.state.db = db
    await db.drop_collection("ic_2627_registrations")
    yield myapp
    await a_close_mongodb()


@pytest_asyncio.fixture()
async def ic_registrations(app):

    def safe_int(value):
        try:
            return int(value)
        except ValueError:
            return 0

    with (Path("tests") / "data" / "ic_registrations.csv").open() as regf:
        reader = DictReader(regf)
        for row in reader:
            await app.state.db.ic_2627_registrations.insert_one(
                {
                    "idclub": safe_int(row["idclub"]),
                    "name": row["club"],
                    "teams1": safe_int(row["div1"]),
                    "teams2": safe_int(row["div2"]),
                    "teams3": safe_int(row["div3"]),
                    "teams4": safe_int(row["div4"]),
                    "teams5": safe_int(row["div5"]),
                    "teams6": safe_int(row["div6"]),
                    "wishes": {},
                    # add other fields as necessary
                }
            )
