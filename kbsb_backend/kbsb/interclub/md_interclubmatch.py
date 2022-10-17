# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

from datetime import datetime
from enum import Enum
from inspect import signature
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from reddevil.core import DbBase, DocumentType, ListType


class GameResult(str, Enum):
    homewins = "1-0"
    draw = "½-½"
    visitwins = "0-1"
    FF1_0 = "1-0 FF"
    FF0_1 = "0-1 FF"
    FF0_0 = "0-0 FF"
    empty = ""


class Party(str, Enum):
    home = "Home"
    visit = "Visit"
    itd = "Interclub Tournament Director"


class ResultChange(str, Enum):
    plan = "HomePlanning"
    fillresult = "FillResult"
    changeresult = "ChangeResult"
    changeplayer = "Changeplayer"
    oldimport = "ImportedFromOldWebsite"


class MatchSignature(BaseModel):
    idclub: int
    idnumber: int
    party: str
    signdate: datetime


class ResultChange(BaseModel):
    boardnumber: int
    writer: Party
    kind: ResultChange
    idexecutor: int
    idclub: int
    details: str
    changedate: datetime


class InterclubBoard(BaseModel):
    idnumber_home: int
    idnumber_visit: int
    boardnumber: int
    playername_home: str
    playername_visit: str
    playerrating_home: int
    playerrating_visit: int
    result: GameResult


class InterclubMatch(DocumentType):
    round: int
    division: int
    series: str
    pairing: int
    id: str
    club_home: int
    club_visit: int
    boards: List[InterclubBoard]
    signatures: List[MatchSignature]


class InterclubMatchOptional(DocumentType):
    round: Optional[int]
    division: Optional[int]
    series: Optional[str]
    pairing: Optional[int]
    id: Optional[str]
    club_home: Optional[int]
    club_visit: Optional[int]
    boards: Optional[List[InterclubBoard]] = []
    signatures: Optional[List[MatchSignature]] = []


class InterclubMatchList(ListType):
    matches: List[InterclubMatch]


class DbInterclubMatch(DbBase):
    COLLECTION = "interclubmatch"
    DOCUMENTTYPE = "InterclubMatch"
    VERSION = 1
    IDGENERATOR = "uuid"
    DT = InterclubMatch
    LT = InterclubMatchList
    ItemField = "matches"
