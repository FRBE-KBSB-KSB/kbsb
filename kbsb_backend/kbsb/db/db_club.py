# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

from reddevil.db.db_base import DbBase

class DbClub(DbBase):
    COLLECTION = "club"
    DOCUMENTTYPE = "Club"
    VERSION = 1
    IDGENERATOR = "objectid"

