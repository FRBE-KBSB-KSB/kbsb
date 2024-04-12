# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from reddevil.core import DbBase, DocumentType, ListType
from .md_interclubclub import InterclubTeam

class InterclubSeries(DocumentType):
    """
    representation of a single series
    """

    division: int
    index: str
    teams: List[InterclubTeam]


class InterclubSeriesList(ListType):
    allseries: List[InterclubSeries]


class DbInterclubSeries(DbBase):
    COLLECTION = "interclubseries"
    DOCUMENTTYPE = "InterclubSeries"
    VERSION = 1
    IDGENERATOR = "uuid"
    DT = InterclubSeries
    LT = InterclubSeriesList
    ItemField = "allseries"
