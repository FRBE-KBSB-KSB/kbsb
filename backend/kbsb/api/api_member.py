import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from reddevil.common import url, RdException
from reddevil.service.security import bearer_schema, validate_token 
from kbsb.service.member import (
    getMemberAnon,
    getMemberBasic,
    getMemberFull,
)
from kbsb.models.md_member import (
    MemberAnon,
    MemberBasic,
    MemberOptional,
)
from kbsb import app, url

log = logging.getLogger('kbsb')

# @app.get(url + '/members', response_model=MemberListOut)
# async def api_getMembers(picture: int=0, 
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         return await getMembers({'picture': picture})
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call get_members')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.post(url + '/members', response_model=str)
# async def api_createMember(p: MemberIn,
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         return await createMember(p)
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call create_member')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(url + '/member/{id}', response_model=MemberOptional)
def api_getMember(id: str, 
    auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
):
    try:
        validate_token(auth)
        return getMemberFull(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception('failed api call getMember')
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(url + '/member/{id}/basic', response_model=MemberBasic)
def api_getMemberBasic(id: str, 
    auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
):
    try:
        validate_token(auth)
        return getMemberBasic(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception('failed api call getMember')
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(url + '/member/{id}/anon', response_model=MemberAnon)
def api_getMemberAnon(id: str):
    try:
        return getMemberAnon(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception('failed api call getMemberAnon')
        raise HTTPException(status_code=500, detail="Internal Server Error")


# @app.get(url + '/a/member/{id}', response_model=MemberOptional)
# async def api_anon_getMember(id: str, picture: int=0):
#     try:
#         return await getMember(id, {'picture': picture})
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call get_member')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.delete(url + '/member/{id}')
# async def api_deleteMember(id: str, 
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         await deleteMember(id)
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call delete_member')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.put(url + '/member/{id}')
# async def api_updateMember(id: str, p: MemberUpdate, 
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         await updateMember(id, p)
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call update_member')
#         raise HTTPException(status_code=500, detail="Internal Server Error")
