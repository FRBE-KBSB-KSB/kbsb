# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

from reddevil.db.db_base import DbBase

class DbInterclubPrevious(DbBase):
    COLLECTION = "interclubprevious"
    DOCUMENTTYPE = "InterclubPrevious"
    VERSION = 1
    IDGENERATOR = "uuid"

class DbInterclubEnrollment(DbBase):
    COLLECTION = "interclubenrollment"
    DOCUMENTTYPE = "InterclubEnrollment"
    VERSION = 1
    IDGENERATOR = "uuid"