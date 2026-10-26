import asyncio

import click
from dotenv import load_dotenv
from fastapi import FastAPI
from reddevil.core import (
    get_settings,
    register_app,
)

from kbsb.main import lifespan
from kbsb.member.member import odoo_email2idbel

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
load_dotenv()
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


async def email_to_idbel(email: str):
    async with lifespan(app):
        idbel = await odoo_email2idbel(email, app)
    return idbel


@click.command()
@click.argument("email")
def main(email: str):
    idbel = asyncio.run(email_to_idbel(email))
    click.echo(f"email: {email}, idbel: {idbel}")


if __name__ == "__main__":
    main()
