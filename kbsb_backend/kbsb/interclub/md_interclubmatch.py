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


class Party(str, Enum):
    home = "Home"
    visit = "Visit"
    itd = "Interclub Tournament Director"

class ResultChange(str, Enum):
    plan = "HomePlanning"
    fillresult = "FillResult"
    changeresult = "ChangeResult"
    changeplayer = "Changeplayer"


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
    number: int
    home_id: int
    home_firstname: str
    home_lastname: str
    visit_id: int
    visit_firstname: str
    visit_lastname: str
    result: GameResult


class InterclubMatch(DocumentType):
    boards: List[InterclubBoard]
    division: int
    home_clb: int
    index: str
    round: int
    signatures: List[MatchSignature]
    visit_clb: int


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
