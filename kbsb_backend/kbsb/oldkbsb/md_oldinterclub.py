# copyright Ruben Decrop 2012 - 2021

from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Integer, String, Date
from datetime import date
from typing import List


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

    id: int = Field(sa_column=Column("Id", Integer, primary_key=True))
    round_nr: int = Field(sa_column=Column("Num_Rnd", Integer))
    round_date: date = Field(sa_column=Column("Date_Rnd", Date))
    division: int = Field(sa_column=Column("Division", Integer))
    series: str = Field(sa_column=Column("Serie", String))
    board: int = Field(sa_column=Column("Tableau", Integer))
    club_home: int = Field(sa_column=Column("Num_Club1", Integer))
    idnumnber_home: int = Field(sa_column=Column("Matricule1", Integer))
    playername_home: str = Field(sa_column=Column("Nom_Joueur1", String))
    playerrating_home: int = Field(sa_column=Column("Elo_Icn1", Integer))
    team_home: int = Field(sa_column=Column("id_Equ1", Integer))
    club_visit: int = Field(sa_column=Column("Num_Club2", Integer))
    idnumnber_visit: int = Field(sa_column=Column("Matricule2", Integer))
    playername_visit: str = Field(sa_column=Column("Nom_Joueur2", String))
    playerrating_visit: int = Field(sa_column=Column("Elo_Icn2", Integer))
    team_visit: int = Field(sa_column=Column("id_Equ2", Integer))
    score: str = Field(sa_column=Column("Score", String))


class OldInterclubGamesList(SQLModel):
    games: List[OldInterclubGames]
