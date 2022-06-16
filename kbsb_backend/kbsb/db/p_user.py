# copyright Ruben Decrop 2022

# We define the p_clubs ao the old  myssql database in SQLALchemy

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class P_User(Base):
    __tablename__ = "p_user"

    user = Column('user', String, primary_key=True)
    password = Column("password")