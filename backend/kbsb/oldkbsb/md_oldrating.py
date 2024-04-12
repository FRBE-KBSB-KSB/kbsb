# copyright Ruben Decrop 2012 - 2021

from sqlalchemy import Column, String, Integer
from typing import Optional
from pydantic import BaseModel
from .md_old import Base

class OldNatRating_sql(Base):
    __tablename__ = "p_player202207"

    idnumber = Column("Matricule", Integer, primary_key=True)
    idfide = Column("Fide", Integer)
    natrating = Column("Elo", Integer)
    nationality = Column("Nat", String)


class OldNatRating(BaseModel):

    idnumber: int
    idfide: Optional[int]
    natrating: int = 0
    nationality: str

    class Config:
        orm_mode = True


class OldFideRating_sql(Base):
    __tablename__ = "fide"

    idfide = Column("ID_NUMBER", Integer, primary_key=True)
    fiderating = Column("ELO", Integer)


class OldFideRating(BaseModel):

    idfide: int
    fiderating: int = 0

    class Config:
        orm_mode = True

