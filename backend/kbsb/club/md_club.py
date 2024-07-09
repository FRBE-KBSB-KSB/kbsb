# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from reddevil.core import DbBase


class Visibility(str, Enum):
    hidden = "HIDDEN"  # only by member itself and by KBSB baord
    club = "CLUB"  # hidden + club members can view
    public = "PUBLIC"  # open to everyone


class Federation(str, Enum):
    v = "V"
    f = "F"
    d = "D"


class ClubRoleNature(str, Enum):
    ClubAdmin = "ClubAdmin"
    InterclubAdmin = "InterclubAdmin"
    InterclubCaptain = "InterclubCaptain"


class Day(str, Enum):
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"
    saturday = "Saturday"
    sunday = "Sunday"


class ClubMember(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    email_visibility: Visibility | None = None
    idnumber: int
    mobile: str | None = None
    mobile_visibility: Visibility | None = None


class ClubRole(BaseModel):
    nature: ClubRoleNature
    memberlist: list[int]  # list of id numbers that have the role


class Club(BaseModel):
    """
    basic club used in service layer
    """

    address: str | None = ""  # full contact address
    bankaccount_name: str | None = ""
    bankaccount_iban: str | None = ""
    bankaccount_bic: str | None = ""
    boardmembers: dict[str, ClubMember] | None = None
    clubroles: list[ClubRole] | None = None
    email_admin: str | None = ""  # email address for administrative tasks
    email_finance: str | None = ""  # email address for financial tasks
    email_interclub: str | None = ""  # email_fdor interclub tasks
    email_main: str | None = ""  # main email address to contact, must be available
    enabled: bool | None = True
    federation: Federation | None = None
    idclub: int | None = 0
    id: str | None = ""
    name_long: str | None = ""  # long name without abbrevioations
    name_short: str | None = ""  # short name with abbreviations
    openinghours: dict[Day, str] | None = None
    venue: str | None = ""  # full multiline address of playing venue
    website: str | None = ""


class ClubHistory(BaseModel):
    action: str
    label: str
    idclub: str
    time: datetime


class ClubIn(BaseModel):
    """
    Validator for inserting a club
    """

    address: str | None = ""  # full contact address
    bankaccount_name: str | None = ""
    bankaccount_iban: str | None = ""
    bankaccount_bic: str | None = ""
    boardmembers: dict[str, ClubMember] | None = None
    clubroles: list[ClubRole] | None = None
    email_admin: str | None = ""  # email address for administrative tasks
    email_finance: str | None = ""  # email address for financial tasks
    email_interclub: str | None = ""  # email_fdor interclub tasks
    email_main: str | None = ""  # main email address to contact, must be available
    enabled: bool | None = True
    federation: Federation
    idclub: int
    name_long: str  # long name without abbrevioations
    name_short: str  # short name with abbreviations
    openinghours: dict[Day, str] | None = None
    venue: str | None = ""  # full multiline address of playing venue
    website: str | None = ""


class ClubUpdate(BaseModel):
    """
    Validator for updating a club
    """

    address: str | None = None  # full contact address
    bankaccount_name: str | None = None
    bankaccount_iban: str | None = None
    bankaccount_bic: str | None = None
    boardmembers: dict[str, ClubMember] | None = None
    clubroles: list[ClubRole] | None = None
    email_admin: str | None = None
    email_finance: str | None = None
    email_interclub: str | None = None
    email_main: str | None = None
    federation: Federation | None = None
    name_long: str | None = None
    name_short: str | None = None
    openinghours: dict[Day, str] | None = None
    venue: str | None = None
    website: str | None = None


class ClubItem(BaseModel):
    email_main: str | None = ""
    enabled: bool
    idclub: int
    id: str
    name_long: str
    name_short: str


class ClubAnon(BaseModel):
    address: str | None = ""
    boardmembers: dict[str, ClubMember] | None = None
    email_main: str | None = ""
    email_admin: str | None = ""
    email_finance: str | None = ""
    email_interclub: str | None = ""
    enabled: bool
    idclub: int
    id: str
    name_long: str
    name_short: str
    venue: str | None = ""
    website: str | None = ""


class DbClub(DbBase):
    COLLECTION = "club"
    DOCUMENTTYPE = "Club"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True
