# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


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
    idinvoice: Optional[str]
    idpaymentrequest: Optional[str]
    locale: Optional[str]
    name_long: Optional[str]
    name_short: Optional[str]
    teams1: Optional[int]
    teams2: Optional[int]
    teams3: Optional[int]
    teams4: Optional[int]
    teams5: Optional[int]
    wishes: Optional[Dict]


class InterclubEnrollmentList(BaseModel):
    enrollments: List[Any]


class InterclubEnrollmentIn(BaseModel):
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    wishes: dict


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
