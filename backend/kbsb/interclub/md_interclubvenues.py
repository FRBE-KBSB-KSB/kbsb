# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from reddevil.core import DbBase, DocumentType, ListType


class InterclubVenue(BaseModel):
    address: str
    email: str
    phone: str
    capacity: int  # number of boards, 0  is unlimited
    notavailable: List[str]


class InterclubVenuesIn(BaseModel):
    venues: List[InterclubVenue]


class InterclubVenues(BaseModel):
    id: Optional[str]
    idclub: Optional[int]
    name_long: Optional[str]
    name_short: Optional[str]
    venues: List[InterclubVenue]


class InterclubVenuesList(BaseModel):
    clubvenues: List[Any]


class DbInterclubVenues(DbBase):
    COLLECTION = "interclubvenues"
    DOCUMENTTYPE = "InterclubVenues"
    VERSION = 1
    IDGENERATOR = "uuid"
