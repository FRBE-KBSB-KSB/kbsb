# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from enum import Enum


# Table p_clubs
#     Column('Club', INTEGER(display_width=10, unsigned=True), table=<p_clubs>, primary_key=True, nullable=False, server_default=DefaultClause(<sqlalchemy.sql.elements.TextClause object at 0x7f731abf9280>, for_update=False)),
#     Column('Federation', CHAR(collation='latin1_general_cs', length=1), table=<p_clubs>),
#     Column('Ligue', SMALLINT(display_width=6), table=<p_clubs>),
#     Column('Intitule', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>),
#     Column('Abbrev', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>),
#     Column('Local', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>),
#     Column('Adresse', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>),
#     Column('CodePostal', VARCHAR(collation='latin1_general_cs', length=10), table=<p_clubs>),
#     Column('Localite', VARCHAR(collation='latin1_general_cs', length=50), table=<p_clubs>),
#     Column('Telephone', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>),
#     Column('SiegeSocial', VARCHAR(collation='latin1_general_cs', length=250), table=<p_clubs>),
#     Column('JoursDeJeux', VARCHAR(collation='latin1_general_cs', length=220), table=<p_clubs>),
#     Column('WebSite', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>),
#     Column('WebMaster', VARCHAR(collation='latin1_general_cs', length=50), table=<p_clubs>),
#     Column('Forum', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>),
#     Column('Email', VARCHAR(collation='latin1_general_cs', length=60), table=<p_clubs>),
#     Column('Mandataire', INTEGER(display_width=11), table=<p_clubs>, comment='0=aucun 1=Fede 2=Ligue 3=Club 4=Matricule'),
#     Column('MandataireNr', INTEGER(display_width=11), table=<p_clubs>),
#     Column('PresidentMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('ViceMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('TresorierMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('SecretaireMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('TournoiMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('JeunesseMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('InterclubMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('BqueTitulaire', VARCHAR(collation='latin1_general_cs', length=120), table=<p_clubs>),
#     Column('BqueCompte', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>),
#     Column('BqueBIC', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>),
#     Column('Divers', VARCHAR(collation='latin1_general_cs', length=250), table=<p_clubs>),
#     Column('ModifMat', INTEGER(display_width=11), table=<p_clubs>),
#     Column('ModifDate', DATE(), table=<p_clubs>),
#     Column('CreDate', DATE(), table=<p_clubs>),
#     Column('SupDate', DATE(), table=<p_clubs>)


class Visibility(str, Enum):
    hidden = "HIDDEN"  # only by member itself and by KBSB baord
    club = "CLUB"  # club members are added
    public = "PUBLIC"  # to everyone


class Federation(str, Enum):
    v = "V"
    f = "F"
    d = "D"


class Day(str, Enum):
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"
    saturday = "Saturday"
    sunday = "Sunday"


class Opening:
    day: Day
    starthour: str
    endhour: str
    nature: str  # youth, adult, main


class BoardMember(BaseModel):
    first_name: str
    last_name: str
    email: str
    mobile: str
    email_visibility: Visibility
    mobile_visibility: Visibility


class Club(BaseModel):
    """
    basic club used in service layer
    """

    address: str  # full contact address
    bankaccount_name: str
    bankaccount_iban: str
    bankaccount_bic: str
    boardmembers: List(BoardMember)
    email_admin: str  # email address for administrative tasks
    email_finance: str  # email address for financial tasks
    email_interclub: str  # email_fdor interclub tasks
    email_main: str  # main email address to contact, must be available
    enabled: bool
    federation: Federation
    idclub: int
    id: str
    name_long: str  # long name without abbrevioations
    name_short: str  # short name with abbreviations
    openinghours: List[Opening]
    venue: str  # full multiline address of playing venue
    website: str


class ClubHistory(BaseModel):
    action: str
    label: str
    idclub: str
    time: datetime


class ClubOptional(BaseModel):
    """
    Primary class used in service level to represent a club
    all fields are optional
    """

    address_postal_code: Optional[str]
    address_street: Optional[str]
    address_town: Optional[str]
    address_venue: Optional[str]
    bankaccount_name: Optional[str]
    bankaccount_iban: Optional[str]
    bankaccount_bic: Optional[str]
    creation_date: Optional[date]
    email: Optional[str]
    federation: Optional[str]
    forum: Optional[str]
    id: Optional[str]
    playdates: Optional[str]
    registered_office: Optional[str]
    remarks: Optional[str]
    removal_date: Optional[date]
    short_name: Optional[str]
    webmaster: Optional[str]
    website: Optional[str]


class ClubBasic(BaseModel):
    """
    Validator for only Basic fields
    """

    address_postal_code: Optional[str] = ""
    address_street: Optional[str] = ""
    address_town: Optional[str] = ""
    address_venue: Optional[str] = ""
    email: Optional[str] = ""
    federation: str
    id: str
    id_president: Optional[str] = ""
    id_vicepresident: Optional[str] = ""
    id_treasurer: Optional[str] = ""
    id_secretary: Optional[str] = ""
    id_tournament: Optional[str] = ""
    id_youth: Optional[str] = ""
    id_interclub: Optional[str] = ""
    league: str
    long_name: str
    short_name: str
    webmaster: Optional[str] = ""
    website: Optional[str] = ""
