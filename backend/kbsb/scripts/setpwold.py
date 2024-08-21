import asyncio
import asyncclick as click
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    connect_mongodb,
    close_mongodb,
)

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")

from kbsb.member import (
    old_userpassword,
    OldUserPasswordValidator,
)


@click.command()
@click.option("-i", "--id", "user", help="ID user", required=True)
@click.option("-p", "--password", help="Password", required=True)
@click.option("-c", "--club", help="Club number", required=True, type=int)
@click.option("-e", "--email", help="Email user", required=True)
async def set_oldpassword(user, password, club, email):
    """
    set the user password on the old mysql database
    """
    # await connect_mongodb()
    await old_userpassword(
        OldUserPasswordValidator(user=user, password=password, club=club, email=email)
    )
    # await close_mongodb()


if __name__ == "__main__":
    asyncio.run(set_oldpassword())
