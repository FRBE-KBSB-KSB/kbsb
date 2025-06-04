# copyright Ruben Decrop 2012 - 2025

# all models in the service level exposed to the API
# we are using pydantic as tool

from pydantic import BaseModel


class SwarDateItem(BaseModel):
    DateValue: str  # date format dd/mm/yyyy


class SwarTBType(BaseModel):
    Type: str


class SwarTrnDescription(BaseModel):
    Version: str
    Tournament: str
    Organizer: str | None
    ClubOrLogo: str | None
    Place: str | None
    Arbiter_1: str | None
    Arbiter_2: str | None
    Arbiter_3: str | None
    Arbiter_4: str | None
    StartDate: str | None  # date format dd/mm/yyyy
    EndDate: str | None  # date format dd/mm/yyyy
    RateOfPlay: str | None
    NbOfRounds: int
    SepareteCategories: int | None = 0
    TournamentType: str | None
    AmericainPresence: int | None = 0
    MultiplePairing: int | None = 0
    FirstTableNumber: int | None = 1
    SW321_Win: str | None = "0.0"
    SW321_Null: str | None = "0.0"
    SW321_Loss: str | None = "0.0"
    SW321_Bye: str | None = "0.0"
    SW321_Presence: str | None = "0.0"
    EloUsed: str | None = ""
    TournamentStd: str | None = ""
    ByeValue: str | None = "1"
    AbsValue: str | None = "½"
    NumberOfTimes: str | None = "0"
    ToRound: str | None = "0"
    Federation: str | None = ""
    NbDates: int | None = 1
    NbPlayers: int | None = 0
    DatesArray: list[SwarDateItem] | None = []
    TieBreaks: list[SwarTBType] | None = []
    Category: str | None = ""
    Category_1: list[dict] | None = []
    Category_2: list[dict] | None = []
    Category_3: list[dict] | None = []


class SwarTBPlayer(BaseModel):
    Type: str | None = ""
    Points: str | None = "0.0"


class SwarRoundItem(BaseModel):
    RoundNr: int = 0
    Tabel: str | None = ""
    OpponentNi: str | None = ""
    OpponentName: str | None = ""
    Result: str | None = "0"
    Color: str | None = ""
    Float: str
    XtraPts: str | None = "0.0"


class SwarPlayer(BaseModel):
    Ranking: int = 0
    Name: str
    Ni: int = 0
    Rank: int = 0
    CatIndex: int = 0
    CategoryValue_1: str | None = ""
    CategoryValue_2: str | None = ""
    CategoryValue_3: str | None = ""
    CategoryValue_4: str | None = ""
    BirthDate: str | None = ""  # date format dd/mm/yyyy
    Sex: str | None = ""
    Country: str | None = ""
    NationalId: int = 0
    FideId: int = 0
    Payed: int = 1
    Affiliated: int = 1
    NationalElo: int = 0
    FideElo: int = 0
    Titel: str | None = ""
    ClubNumber: int = 0
    ClubName: str | None = ""
    NbOfParts: int = 0
    Points: str | None = "0.0"
    TieBreak: list[SwarTBPlayer] | None = []
    Performance: int = 0
    Paye: int = (1,)
    Absent: str | None = ("",)
    AbsentAtRounds: str | None = ""
    ExtraPts: str | None = "0.0"
    SpecialPts: str | None = "0.0"
    NbRounds: int = 1
    RoundArray: list[SwarRoundItem] | None = []


class SwarT(BaseModel):
    TournamentDesc: SwarTrnDescription
    Player: list[SwarPlayer]


class SwarTournament(BaseModel):
    Swar: SwarT
