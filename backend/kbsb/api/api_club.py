import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from reddevil.common import url, RdException
from reddevil.service.security import bearer_schema, validate_token 
from kbsb.service.club import (
    getClubBasic,
    getClubFull,
)
from kbsb.models.md_club import (
    ClubOptional,
    ClubBasic
)
from kbsb import app, url

log = logging.getLogger('kbsb')

# @app.get(url + '/clubs', response_model=ClubListOut)
# async def api_getClubs(picture: int=0, 
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         return await getClubs({'picture': picture})
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call get_clubs')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.post(url + '/clubs', response_model=str)
# async def api_createClub(p: ClubIn,
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         return await createClub(p)
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call create_club')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(url + '/club/{id}', response_model=ClubOptional)
def api_getClub(id: str, 
    auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
):
    try:
        # validate_token(auth)
        return getClubFull(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception('failed api call getClub')
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(url + '/club/{id}/basic', response_model=ClubBasic)
def api_getClubBasic(id: str, 
    auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
):
    try:
        # validate_token(auth)
        return getClubBasic(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception('failed api call getClubBasic')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.get(url + '/a/club/{id}', response_model=ClubOptional)
# async def api_anon_getClub(id: str, picture: int=0):
#     try:
#         return await getClub(id, {'picture': picture})
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call get_club')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.delete(url + '/club/{id}')
# async def api_deleteClub(id: str, 
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         await deleteClub(id)
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call delete_club')
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.put(url + '/club/{id}')
# async def api_updateClub(id: str, p: ClubUpdate, 
#     auth: HTTPAuthorizationCredentials=Depends(bearer_schema)
# ):
#     try:
#         await validate_token(auth)
#         await updateClub(id, p)
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception('failed api call update_club')
#         raise HTTPException(status_code=500, detail="Internal Server Error")
