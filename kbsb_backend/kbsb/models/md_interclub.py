# copyright Ruben Decrop 2012 - 2021

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
    idclub: int
    name_long: str
    name_short: str
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    idpaymentrequest: str
    idinvoice: str
        
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

