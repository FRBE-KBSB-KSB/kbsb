import logging
from fastapi import APIRouter
from . import (
    SwarTournament,
    TournamentItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/toutnaments")

# API routes for tournament management


@router.get("/", response_model=list[TournamentItem])
async def get_tournaments(): ...


# swar


@router.post("/swar", response_model=str)
async def upload_new_swarfile(): ...


@router.put("/swar/{id}", status_code=201)
async def update_swar(id: str): ...


@router.get("/swar/{id}", response_model=SwarTournament)
async def get_swar(id: str): ...


@router.delete("/swar/{id}", status_code=204)
async def delete_swar(id: str): ...


# pairtwo


@router.post("/pairtwo", response_model=str)
async def upload_new_pairtwo(): ...


@router.put("/pairtwo/{id}", status_code=201)
async def update_pairtwo(id: str): ...


@router.get("/pairtwo/{id}", response_model=SwarTournament)
async def get_pairtwo(id: str): ...


@router.delete("/pairtwo/{id}", status_code=204)
async def delete_pairtwo(id: str): ...


# standard


@router.post("/standard", response_model=str)
async def upload_new_standard(): ...


@router.put("/standard/{id}", status_code=201)
async def update_standard(id: str): ...


@router.get("/pairtwo/{id}", response_model=SwarTournament)
async def get_standard(id: str): ...


@router.delete("/pairtwo/{id}", status_code=204)
async def delete_standard(id: str): ...


# eloprocessing


@router.get("/bel_elo/{id}")
async def get_belelo_trn(id: str): ...


@router.get("/fid_eelo/{id}")
async def get_belelo_trn(id: str): ...


@router.post("/cmd/process_bel_elo/{id}", status_code=201)
async def process_bel_elo(): ...


@router.post("/cmd/process_fide_elo/{id}", status_code=201)
async def process_fide_elo(): ...


@router.post("/cmd/send_bel_elo/{id}", status_code=201)
async def send_bel_elo(): ...


@router.post("/cmd/send_fide_elo/{id}", status_code=201)
async def send_fide_elo(): ...
