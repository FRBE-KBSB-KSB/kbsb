# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from enum import Enum


class InterclubPlayer(BaseModel):
    """
    Player on player list of a club
    """

    first_name: str
    last_name: str
    idnumber: int
    belrating: int
    fiderating: int
    assignedrating: int


class InterclubTeam(BaseModel):
    idclub: int
    division: int
    serie: str
    effective: List[InterclubPlayer]


class InterclubSerie(BaseModel):
    """
    representation of
    """

    division: int
    serie: str
    teams: List[InterclubTeam]


class InterclubEnrollment(BaseModel):
    id: Optional[str]
    idclub: Optional[int]
    locale: Optional[str]
    name_long: Optional[str]
    name_short: Optional[str]
    teams1: Optional[int]
    teams2: Optional[int]
    teams3: Optional[int]
    teams4: Optional[int]
    teams5: Optional[int]
    idpaymentrequest: Optional[str]
    idinvoice: Optional[str]


class InterclubEnrollmentList(BaseModel):
    enrollments: List[Any]


class InterclubEnrollmentIn(BaseModel):
    idclub: int
    locale: Optional[str] = "nl"
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int


class InterclubEnrollmentUpdate(BaseModel):
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int


class InterclubPrevious(BaseModel):
    idclub: int
    name_long: str
    name_short: str
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    promotionFrom: Optional[List[int]] = None
    degradationFrom: Optional[List[int]] = None
    stopped: Optional[List[int]] = None
