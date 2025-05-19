# copyright Ruben Decrop 2012 - 2025

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from datetime import datetime
from pydantic import BaseModel
from enum import StrEnum, auto


class TrnStatus(StrEnum):
    NOTSTARTED = auto()
    STARTED = auto()
    ENDED = auto()
    PROCESSED = auto()
    ARCHIVED = auto()


class OrganizerKind(StrEnum):
    CLUB = auto()
    FEDERATION = auto()
    LEAGUE = auto()
    OTHER = auto()

class Gender(StrEnum):
    M = auto()
    F = auto()
    X = auto()  # yep we are a bit woke

class EloPrecedence(StrEnum):
    FIDE = auto()
    BEL = auto()
    MAX = auto()  # max rating of the player, used in some tournaments

class TrnPlayer(BaseModel):
    birthyear: int
    chesstitle: str  # chesstitle at the start of the tournament
    extra: dict  # all non essential fiields clubid, shoe size
    first_name: str
    gender: Gender
    idbel: str  # as one cannot do maths with IDs, IDs are strings by nature
    idfide: str  # as one cannot do maths with IDs, IDs are strings by nature
    last_name: str
    ratingbel: int  # rating at the start of tournament
    ratingfide: int  # rating at the start of tournament

class TrnTeam(BaseModel):
    players: list[TrnPlayer]
    name: str
    players_per_encounter: int  # how many players are actually playing at the same time


class TrnSystem(StrEnum):
    SWISS = auto()
    ROUNDROBIN = auto()
    DOUBLEROUNDROBIN = auto()
    LOOSEGAMES = auto()

class TrnRound(BaseModel):
    nround: int
    play_datetime: datetime 
    all_played: bool
    all_eloprocessed: bool 


class Tournament(BaseModel):
    """
    Model as defined in the database, no validation whatsoever
    """

    name: str
    start_date: date
    end_date: date
    rounds: 
    status: TrnStatus
    id: str
    organizer: int
    organizer_name: str
    organizer_kind: OrganizerKind
    players: list[TrnPlayer]
    eloprecedence: EloPrecedence
    trn_sysem: TrnSystem
    team_event: bool
    players_per_team: int
    pairingsystem: str
    venue: str
    players: list[TrnPlayer]
    teams: list[TrnTeam]

