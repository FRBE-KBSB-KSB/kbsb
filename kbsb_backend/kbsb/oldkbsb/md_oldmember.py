# copyright Ruben Decrop 2012 - 2022

from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import declarative_base
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from .md_old import Base


class OldMember_sql(Base):
    """
    table signaletique in mysql
    we only encode the fields we need
    """

    __tablename__ = "signaletique"

    birthdate = Column("Dnaiss", Date)
    deceased = Column("Decede", Integer)
    email = Column("Email", String(48))
    first_name = Column("Prenom", String)
    gender = Column("Sexe", String)
    idclub = Column("Club", Integer, index=True)
    idnumber = Column("Matricule", Integer, primary_key=True)
    last_name = Column("Nom", String)
    licence_g = Column("G", Integer)
    locked = Column("Locked", Integer)
    mobile = Column("Gsm", String)
    year_affiliation = Column("AnneeAffilie", Integer, index=True)


class OldMember(BaseModel):
    birthdate: Optional[date]
    deceased: Optional[int]
    email: Optional[str]
    first_name: Optional[str]
    gender: Optional[str]
    idclub: Optional[int]
    idnumber: Optional[int]
    last_name: Optional[str]
    licence_g: Optional[int]
    locked: Optional[int]
    mobile: Optional[str]
    year_affiliation: Optional[int]

    class Config:
        orm_mode = True


class OldMemberList(BaseModel):
    members: List[OldMember]


class ActiveMember(BaseModel):
    idclub: int
    idnumber: int
    first_name: str
    last_name: str
    natrating: int = 0
    fiderating: int = 0


class ActiveMemberList(BaseModel):
    activemembers: List[ActiveMember]
