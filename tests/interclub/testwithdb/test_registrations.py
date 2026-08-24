from pathlib import Path

import pytest

testdatadir = Path("tests") / "data"


@pytest.mark.asyncio
async def test_connection(app):
    db = app.state.db
    await db.testcoll.insert_one({"idclub": "750"})


@pytest.mark.asyncio
async def test_read_registration(app, ic_registrations):
    db = app.state.db
    reg = await db.ic_2627_registrations.find_one({"idclub": 750})
    assert reg is not None
    assert reg["name"] == "Club 750"
    assert reg["idclub"] == 750
    assert reg["teams1"] == 1
