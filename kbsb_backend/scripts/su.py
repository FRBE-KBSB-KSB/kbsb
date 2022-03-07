import asyncio

from datetime import date, datetime, timedelta, timezone
from kbsb.crud import get_db
from kbsb import settings
from reddevil.service.sv_account import createAccount
from reddevil.models.md_account import AccountIn, LoginType

async def main():
    """
    create a superaccount
    """


    # create account
    await createAccount(AccountIn(
        email='',
        enabled=True,
        first_name='',
        id='eddy',
        last_name='',
        locale='',
        logintype=LoginType.email,
        password='kannibaal',
    ))


if __name__ == '__main__':
    asyncio.run(main())
