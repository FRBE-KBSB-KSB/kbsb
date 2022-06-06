# copyright Ruben Decrop 2012 - 2021

# validator models for the old models

from pydantic import BaseModel

class OldLogin(BaseModel):
    idnumber: int
    password: str