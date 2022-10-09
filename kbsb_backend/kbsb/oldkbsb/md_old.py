# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import declarative_base
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from kbsb.core.db import get_mysql


Base = declarative_base()

from .md_oldmember import *
from .md_oldclub import *
from .md_oldrating import *
from .md_oldinterclub import *
from .md_olduser import *
