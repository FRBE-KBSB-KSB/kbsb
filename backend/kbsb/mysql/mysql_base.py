# copyright Chessdevil Consulting BVBA 2015 - 2019

import logging
import uuid
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.sql import select
from sqlalchemy.engine import RowProxy
from kbsb.mysql import engine, metadata
from reddevil.common import RdNotFound, RdBadRequest, RdInternalServerError

log = logging.getLogger('kbsb')

class DbBase:
    """
    Base class for MySQL databases operations
    Input parameters are scalars, stringified ids and dicts
    Output parameters are scalars, stringigfied ids and dicts
    All operations are dumb, unaware of any business logic
    RdExceptions can be raised   
    """

    TABLENAME: Optional[str] = None    # should be overriden
    VERSION = 1

    # @classmethod
    # def add(cls, doc_in: dict ) -> str:
    #     """
    #     create a new record, starting form doc_in, return the id 
    #     """
    #     coll = get_db()[cls.COLLECTION]
    #     if 'id' in doc_in:
    #         doc_in['_id'] = cls.id_to_native(doc_in.pop('id'))
    #     else:
    #         doc_in['_id'] = cls.idgenerator()
    #     doc_in['_documenttype'] = cls.DOCUMENTTYPE
    #     doc_in['_version'] = cls.VERSION
    #     doc_in['_creationtime'] = datetime.now(timezone.utc)
    #     doc_in['_modificationtime'] = datetime.now(timezone.utc)
    #     try:
    #         await coll.insert_one(doc_in)
    #     except:
    #         log.exception(f'error inserting {cls.COLLECTION} record')
    #         raise RdBadRequest(description=f"CannotCreate{cls.COLLECTION}")
    #     return doc_in['_id']

    # @classmethod
    # def find_multiple(cls, options: dict={}) -> List[dict]:
    #     """
    #     get all records
    #     """
    #     table = get_db()[cls.COLLECTION]
    #     docs = []
    #     if 'id' in options:
    #         options['_id'] = cls.id_to_native(options.pop('id'))
    #     _fieldlist = options.pop('_fieldlist', cls.SIMPLEFIELDS)
    #     projfields = {k:1 for k in _fieldlist} if _fieldlist else {
    #         k:0 for k in cls.HIDDENFIELDS} or None
    #     # if FORCEUPGRADE inject _version in projfields
    #     if cls.FORCEUPGRADE and projfields and ('_version' not in projfields):
    #         projfields['_version'] = 2
    #     async for doc in coll.find(options, projection=projfields):
    #         if cls.FORCEUPGRADE:
    #             oldversion = doc.get('_version', 1)
    #             if projfields and projfields['_version'] == 2:
    #                 # remove _version after injection
    #                 doc.pop('_version', None)
    #             if oldversion != cls.VERSION:
    #                 doc = await cls.upgrade(doc, projfields, oldversion)
    #         doc['id'] = cls.id_from_native(doc.pop('_id'))
    #         docs.append(doc)
    #     return docs

    @classmethod
    def find_single(cls, options: dict) -> dict:
        """
        find an doc, 
        raises NotFound if nothing is found
        """
        table = metadata.tables.get(cls.TABLENAME)
        fieldlist = options.pop('_fieldlist', None)
        if fieldlist:
            q = select([table.c.get(f) for f in fieldlist])
        else:
            q = select([table])
        for k,v in options.items():
            q = q.where(table.c.get(k).__eq__(v))
        try:
            with engine.connect() as conn:
                row = conn.execute(q).first()
        except Exception:
            log.exception('failed to execute SQL for find_single')
            raise RdInternalServerError()
        if row is None:
            raise RdNotFound()
        return {k:v for (k,v) in row.items()}

    # @classmethod
    # async def update(cls, id: str, docupdate: Dict[str, Any], 
    #         options: dict = {}) -> dict:
    #     """
    #     update an doc
    #     raises NotFound if event is not found
    #     """
    #     coll = get_db()[cls.COLLECTION]
    #     idn = cls.id_to_native(id)
    #     vu = options.pop('_versionupgrade', None)
    #     if vu:
    #         doc = await coll.find_one({'_id': idn}, projection={'_version':1})
    #         doc = await cls.upgrade(doc, None, doc.get('_version', 1))
    #     docupdate['_modificationtime'] = datetime.now(timezone.utc)
    #     extraupdates = options.pop('$set', None)
    #     if extraupdates:
    #         docupdate.update(extraupdates)
    #     doc = await coll.find_one_and_update(
    #         {'_id': idn},
    #         dict(**{'$set': docupdate}, **options),
    #         projection={k:0 for k in cls.HIDDENFIELDS},
    #         return_document=ReturnDocument.AFTER)
    #     if not doc:
    #         raise RdNotFound(description=f"CannotFind{cls.COLLECTION}")
    #     doc['id'] =  cls.id_from_native(doc.pop('_id'))
    #     return doc

    # @classmethod
    # async def delete(cls, id: str) -> None:
    #     """
    #     delete an doc
    #     """
    #     coll = get_db()[cls.COLLECTION]
    #     rs = await coll.delete_one({'_id': cls.id_to_native(id)})
    #     if rs.deleted_count != 1:
    #         raise RdNotFound(description=f"CannotFind{cls.COLLECTION}")

    # @classmethod
    # async def upgrade(cls, doc: dict, projfields: Optional[dict],  
    #     from_version: int = 1
    # ) -> dict:
    #     """
    #     upgrade the document to version 
    #     """
    #     return doc
                

