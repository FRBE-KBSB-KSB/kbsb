# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from reddevil.core import DbBase, DocumentType, ListType

# interclubclub


class InterclubTeam(BaseModel):
    division: int
    titular: List[int]
    idclub: int
    index: str
    name: str  # includes number like "KOSK 1"
    pairingnumber: int
    playersplayed: List[int]


class InterclubPlayer(BaseModel):
    """
    Player on player list of a club
    """

    assignedrating: int
    fiderating: int
    first_name: str
    idnumber: int
    idclub: int
    last_name: str
    natrating: int
    transfer_confirmed: Optional[bool] = None
    transfer: bool = False


class InterclubTransfer(BaseModel):
    """
    players which are playing for another club
    """

    confirmed_date: Optional[datetime]
    first_name: str
    idnumber: int
    idoriginalclub: int
    idvisitingclub: int
    last_name: str
    request_date: Optional[datetime]

class InterclubClubOptional(BaseModel):
    name: Optional[str]
    idclub: Optional[int]
    teams: Optional[List[InterclubTeam]]
    players: Optional[List[InterclubPlayer]]
    transfersout: Optional[List[InterclubTransfer]]


class InterclubClub(DocumentType):
    name: str
    id: Optional[str]
    idclub: int
    teams: List[InterclubTeam]
    players: List[InterclubPlayer]
    transfersout: List[InterclubTransfer]


class InterclubClubList(ListType):
    clubs: List[InterclubClub]


class DbInterclubClub(DbBase):
    COLLECTION = "interclubclub"
    DOCUMENTTYPE = "InterclubClub"
    VERSION = 1
    IDGENERATOR = "uuid"
    DT = InterclubClub
    LT = InterclubClubList
    ItemField = "clubs"


class TransferRequestValidator(BaseModel):
    members: List[int]
    idoriginalclub: int
    idvisitingclub: int

