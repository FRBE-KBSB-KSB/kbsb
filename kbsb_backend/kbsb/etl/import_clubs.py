import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session

from reddevil.common import register_app, get_settings

register_app(settingsmodule='kbsb.settings')
settings = get_settings()

settings.SECRETS["mysql"] = {
    "name": "kbsb-mysql_local",
    "manager": "filejson",    
}
settings.SECRETS_PATH = "/home/ruben/develop/secrets/kbsb"

import kbsb.service
from kbsb.db import mysql_engine
from kbsb.db.p_clubs import P_Clubs

class OutputWriter:

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.fd = open(self.filename, 'w')
        return self.fd

    def __exit__(self):
        self.fd.close()




def input_record():
    """
    generator that yields every record from input synchronously
    """
    engine = mysql_engine()
    with Session(engine) as session:
        stmt = select(P_Clubs)
        yield  session.scalars(stmt)

async def output_record():


async def main():
    """
    convert files to new version
    """

    for record in input_record():
        await 
            

        
if __name__ == '__main__':
    asyncio.run(main())
