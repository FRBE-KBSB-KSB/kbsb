import asyncio
from csv import writer

from sqlalchemy import select
from sqlalchemy.orm import Session

from reddevil.common import register_app, get_settings
from reddevil.db import connect_mongodb, close_mongodb, get_mongodb

register_app(settingsmodule='kbsb.settings')
settings = get_settings()
print("settings", settings.SECRETS)

import kbsb.service
from kbsb.db import mysql_engine
from kbsb.db.p_clubs import P_Clubs
from kbsb.models.md_club import ClubIn
from kbsb.service.club import create_club


class MongodbClubWriter:

    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def __aexit__(self, *args):
        await close_mongodb()

    async def write(self, p: P_Clubs):
        email = p.email
        if email:
            email = email.replace("[at]","@")
        c = ClubIn(
            address = p.siegesocial,
            bankaccount_name = p.bquetitulaire,
            bankaccount_iban = p.bquecompter,
            bankaccount_bic = p.bquebic,
            email_admin = "",
            email_finance = "",
            email_interclub = "",
            email_main = email,
            enabled = True,
            federation = p.federation[0],
            idclub = p.club,
            league = p.ligue,
            name_long = p.intitule,
            name_short = p.abbrev,
            openinghours = None,
            venue = f"{p.local}\n{p.adresse}\n{p.codepostal}\n{p.localite}",
            website = p.website,
        )
        await create_club(c)


class MysqlClubs:

    def __init__(self, *args, **kwargs):
        self.engine = mysql_engine()
        session = Session(self.engine)
        stmt = select(P_Clubs)
        self.result = session.scalars(stmt)
        
    def __iter__(self):
        return self.result

    def __next__(self):
        for r in self.result:
            yield r
           

async def main():
    async with MongodbClubWriter() as writer:
        db = await get_mongodb()
        await db.club.drop()
        for record in MysqlClubs():
            print(record.club)
            await writer.write(record)

        
if __name__ == '__main__':
    asyncio.run(main())
