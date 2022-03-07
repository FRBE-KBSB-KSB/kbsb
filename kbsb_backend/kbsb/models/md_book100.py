# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2020

from datetime import datetime
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel

class Book100Optional(BaseModel):
    """
    a Book100 service level
    """
    id: Optional[str] = None
    id_bel: Optional[str] = None
    address: Optional[str] = None
    books: Optional[str] = None  # comma spearated list of languages
    cost: Optional[float] = None
    distribution: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    order: Optional[int] = None
    _id: Optional[str] = None
    _version: Optional[int] = None
    _documenttype: Optional[str] = None
    _creationtime: Optional[datetime] = None
    _modificationtime: Optional[datetime] = None

class Book100In(BaseModel):
    """
    contains the fields to create a new book100 record
    """
    id_bel: str
    address: str
    books: str
    cost: float
    distribution: str
    email: str
    first_name: str
    last_name: str
    mobile: str

class Book100List(BaseModel):
    orders: List[Book100Optional]