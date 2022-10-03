# copyright Ruben Decrop 2012 - 2021

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Integer, String


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
