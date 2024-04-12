# copyright Ruben Decrop 2012 - 2021

from sqlalchemy import Column, String, Integer, Date
from typing import Optional, List
from pydantic import BaseModel
from datetime import date
from .md_old import Base


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
