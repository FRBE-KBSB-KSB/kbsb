import asyncio

import click
from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    get_settings,
    register_app,
)

from kbsb.main import lifespan
from kbsb.member.member import anon_getclubmembers

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
load_dotenv()
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


async def get_member(idbel: int):
    async with lifespan(app):
        members = await anon_getclubmembers(idbel)
    return members


@click.command()
@click.argument("idbel")
def main(idbel: int):
    members = asyncio.run(get_member(idbel))
    click.echo(f"number of members: {len(members)} ")
    for m in members:
        click.echo(f"member: {m}")


if __name__ == "__main__":
    main()
