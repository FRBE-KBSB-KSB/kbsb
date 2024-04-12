# copyright Ruben Decrop 2012 - 2021

from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Integer, String, Date
from datetime import date
from typing import List, Optional


class OldInterclubPlayer(SQLModel, table=True):
    __tablename__ = "i_listeforce"

    idnumber: int = Field(sa_column=Column("Matricule", Integer, primary_key=True))
    full_name: str = Field(sa_column=Column("Nom_Prenom", String))
    idclub_player: int = Field(sa_column=Column("Club_Player", String))
    idclub_interclub: int = Field(sa_column=Column("Club_Icn", Integer))
    natrating: int = Field(sa_column=Column("Elo", Integer))
    fiderating: int = Field(sa_column=Column("Fide", Integer))
    assignedrating: int = Field(sa_column=Column("Elo_Icn", Integer))
    team_name: str = Field(sa_column=Column("Nom_Equ", String))


class OldInterclubGames(SQLModel, table=True):
    __tablename__ = "i_parties"

    id: Optional[int] = Field(sa_column=Column("Id", Integer, primary_key=True))
    round: Optional[int] = Field(sa_column=Column("Num_Rnd", Integer))
    round_date: Optional[date] = Field(sa_column=Column("Date_Rnd", Date))
    division: Optional[int] = Field(sa_column=Column("Division", Integer))
    series: Optional[str] = Field(sa_column=Column("Serie", String))
    pairing: Optional[int] = Field(sa_column=Column("Num_App", Integer)) 
    boardnumber: Optional[int] = Field(sa_column=Column("Tableau", Integer))
    club_home: Optional[int] = Field(sa_column=Column("Num_Club1", Integer))
    idnumber_home: Optional[int] = Field(sa_column=Column("Matricule1", Integer))
    playername_home: Optional[str] = Field(sa_column=Column("Nom_Joueur1", String))
    playerrating_home: Optional[int] = Field(sa_column=Column("Elo_Icn1", Integer))
    team_home: Optional[int] = Field(sa_column=Column("id_Equ1", Integer))
    club_visit: Optional[int] = Field(sa_column=Column("Num_Club2", Integer))
    idnumber_visit: Optional[int] = Field(sa_column=Column("Matricule2", Integer))
    playername_visit: Optional[str] = Field(sa_column=Column("Nom_Joueur2", String))
    playerrating_visit: Optional[int] = Field(sa_column=Column("Elo_Icn2", Integer))
    team_visit: Optional[int] = Field(sa_column=Column("id_Equ2", Integer))
    score: Optional[str] = Field(sa_column=Column("Score", String))


class OldInterclubGamesList(SQLModel):
    games: List[OldInterclubGames]
