# copyright Ruben Decrop 2012 - 2020

import logging, json, os
from datetime import datetime, timezone, date
from typing import List, Optional, Union, cast
from kbsb.crud import DbBook100
from reddevil.common import (
    RdInternalServerError, 
    RdBadRequest,
)
from kbsb.models.md_book100 import (
    Book100In,
    Book100List,
    Book100Optional,
)
from kbsb.service.mail import sendconfirmation_book100

log = logging.getLogger('kbsb')

def encode_book100(e: dict, validator_class=Book100Optional) -> Book100Optional:
    """
    validates the a result row, which is a dict, and converts it to a 
    Book100Optional instance
    """ 
    try:
        eo = validator_class(**e)
    except Exception:
        log.exception('cannot validate Book100')
        raise RdInternalServerError(description='Book100ValidationError')
    return cast(Book100Optional, eo)

async def getBook100(id: str, options: dict= {}) -> Book100List:
    """
    get book100 with all fields 
    """
    validator_class = options.pop('_class', Book100Optional)
    row = await DbBook100.find_single({'id': id})
    return encode_book100(row, validator_class)

async def getBooks100(options: dict= {}) -> Book100List:
    """
    get book100 with all fields 
    """
    validator_class = options.pop('_class', Book100Optional)
    docs = await DbBook100.find_multiple(**options)
    orders = [encode_book100(d, validator_class) for d in docs]
    return Book100List(orders=orders)    

async def createBook100(d: Book100In) -> str:
    """
    create a new BoardRole returning its id
    """
    bd = d.dict()
    bd['order'] = await nextOrder()
    b =  await DbBook100.add(bd)
    log.info(f'order id: {b}')
    try:
        order = await getBook100(b)
    except:
        log.exception('could not get order')
    sendconfirmation_book100(order)
    return b

async def nextOrder() -> int:
    """
    returns a new order number
    """
    bl = await getBooks100()
    orders = bl.orders
    if not orders:
        return 1
    return max([cast(int, o.order) for o in orders]) + 1