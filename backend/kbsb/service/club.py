# copyright Ruben Decrop 2012 - 2020

import logging, json, os
from datetime import datetime, timezone, date
from typing import List, Optional, Union, cast
from kbsb.crud import DbClub
from reddevil.common import (
    RdInternalServerError, 
    RdBadRequest,
)
from kbsb.models.md_club import (
    ClubOptional,
    ClubBasic,
    club_o2n,
)
from kbsb.mysql import map_o2n

log = logging.getLogger('kbsb')

club_n2o = {}
for k,v in club_o2n.items():
    club_n2o[v['name']] = {'name': k}

def encode_club(e: dict, validator_class=ClubOptional) -> ClubOptional:
    """
    validates the a result row, which is a dict, and converts it to a 
    ClubOptional instance
    """ 
    try:
        eo = validator_class(**e)
    except Exception:
        log.exception('cannot validate Club')
        raise RdInternalServerError(description='ClubValidationError')
    return cast(ClubOptional, eo)

def getClubFull(id: str, options: dict= {}) -> ClubOptional:
    """
    get club with all fields 
    """
    try:
        idn = int(id)
    except ValueError:
        raise RdBadRequest(description='IdNotIntegerValue')
    row = DbClub.find_single({club_n2o['id']['name']: idn})
    n = map_o2n(row, club_o2n)
    mp = encode_club(n)
    return mp

def getClubBasic(id: str, options: dict= {}) -> ClubOptional:
    """
    get member basic fields 
    """
    try:
        idn = int(id)
    except ValueError:
        raise RdBadRequest(description='IdNotIntegerValue')
    fieldlist = [club_n2o[f]['name'] for f in 
        ClubBasic.__fields__.keys()]
    row = DbClub.find_single({
        club_n2o['id']['name']: idn, 
        '_fieldlist': fieldlist
    })
    n = map_o2n(row, club_o2n)
    mp = encode_club(n, ClubBasic)
    return mp