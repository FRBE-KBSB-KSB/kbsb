# copyright Ruben Decrop 2012 - 2020

import logging, json, os
from datetime import datetime, timezone, date
from typing import List, Optional, Union, cast
from kbsb.crud import DbMember
from reddevil.common import (
    RdInternalServerError, 
    RdBadRequest,
)

from kbsb.models.md_member import (
    MemberOptional,
    MemberBasic,
    MemberAnon,
    member_o2n,
)
from kbsb.mysql import map_o2n

log = logging.getLogger('kbsb')

member_n2o = {}
for k,v in member_o2n.items():
    member_n2o[v['name']] = {'name': k}


def encode_member(e: dict, validator_class=MemberOptional) -> MemberOptional:
    """
    validates the a result row, which is a dict, and converts it to a 
    MemberOptional instance    
    """
    try:
        eo = validator_class(**e)
    except Exception:
        log.exception('cannot validate Member')
        raise RdInternalServerError(description='MemberValidationError')
    return cast(MemberOptional, eo)

def getMemberFull(id: str, options: dict= {}) -> MemberOptional:
    """
    get member with all fields 
    """
    try:
        idn = int(id)
    except ValueError:
        raise RdBadRequest(description='IdNotIntegerValue')
    row = DbMember.find_single({'Matricule': idn})
    n = map_o2n(row, member_o2n)
    mp = encode_member(n)
    return mp

def getMemberBasic(id: str, options: dict= {}) -> MemberOptional:
    """
    get member basic fields 
    """
    try:
        idn = int(id)
    except ValueError:
        raise RdBadRequest(description='IdNotIntegerValue')
    fieldlist = [member_n2o[f]['name'] for f in 
        MemberBasic.__fields__.keys()]
    row = DbMember.find_single({
        'Matricule': idn, 
        '_fieldlist': fieldlist
    })
    n = map_o2n(row, member_o2n)
    mp = encode_member(n, MemberBasic)
    return mp

def getMemberAnon(id: str, options: dict= {}) -> MemberOptional:
    """
    get member basic fields 
    """
    try:
        idn = int(id)
    except ValueError:
        raise RdBadRequest(description='IdNotIntegerValue')
    fieldlist = [member_n2o[f]['name'] for f in 
        MemberAnon.__fields__.keys()]
    row = DbMember.find_single({
        'Matricule': idn, 
        '_fieldlist': fieldlist
    })
    n = map_o2n(row, member_o2n)
    mp = encode_member(n, MemberAnon)
    return mp    