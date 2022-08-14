# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import declarative_base
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from kbsb.core.db import get_mysql

logger = logging.getLogger(__name__)

Base = declarative_base()


class OldLoginValidator(BaseModel):
    """
    Validator for login entry
    """

    idnumber: int
    password: str


class OldUser_sql(Base):
    """
    table p_user in mysql
    we only encode the fields we need
    """

    __tablename__ = "p_user"

    user = Column("user", String, primary_key=True)
    password = Column("password", String)


class OldUser(BaseModel):
    """
    pydantic model olduser
    """

    user: str
    password: str

    class Config:
        orm_mode = True


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
    year_affiliation: Optional[int]

    class Config:
        orm_mode = True


class OldMemberList(BaseModel):
    members: List[OldMember]
