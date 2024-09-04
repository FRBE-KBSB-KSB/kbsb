# copyright Ruben Decrop 2012 - 2024

import logging

from typing import Any
import openpyxl
import datetime
import yaml
from tempfile import NamedTemporaryFile
from fastapi.responses import Response
from reddevil.filestore.filestore import get_file


from reddevil.core import (
    RdNotFound,
    get_settings,
)

from kbsb.interclubs import (
    ICPlayer,
    ICClubDB,
    ICClubItem,
    ICPlayerUpdate,
    ICPlayerValidationError,
    ICTeam,
    DbICClub,
    DbICSeries,
    PlayerlistNature,
)
from kbsb.interclubs.registrations import find_icregistration
from kbsb.club import get_club_idclub


logger = logging.getLogger(__name__)

settings = get_settings()

# Interclub Clubs, Playerlist and Teams

ONPLAYERLIST = [
    PlayerlistNature.ASSIGNED,
    PlayerlistNature.IMPORTED,
    PlayerlistNature.REQUESTEDIN,
]

# CRUD


async def load_icdata():
    _icd = getattr(load_icdata, "icdata", None)
    if not _icd:
        icdr = await get_file("data", "ic2425.yml")
        _icd = yaml.load(icdr.body, Loader=yaml.SafeLoader)
        setattr(load_icdata, "icdata", _icd)
    return _icd


async def create_icclub(icclub: ICClubDB) -> str:
    """
    create a new InterclubClub returning its id
    """
    icclubdict = icclub.model_dump()
    icclubdict.pop("id", None)
    return await DbICClub.add(icclubdict)


async def get_icclub(options: dict | None = {}) -> ICClubDB | None:
    """
    get IC club by idclub, returns None if nothing found
    filter players for active players
    """
    filter = options.copy()
    filter["_model"] = filter.get("_model", ICClubDB)
    club = await DbICClub.find_single(filter)
    return club


# Business methods


async def anon_getICteams(idclub: int, options: dict = {}) -> list[ICTeam]:
    """
    get all the interclub teams for a club available in all divisions
    """
    series = await DbICSeries.find_multiple({"teams.idclub": idclub})
    teams = []
    for s in series:
        for t in s.teams:
            if t.idclub == idclub:
                teams.append(t)
    return teams


async def anon_getICclub(idclub: int, options: dict[str, Any] = {}) -> ICClubDB | None:
    """
    get IC club by idclub, returns None if nothing found
    filter players for active players
    """
    filter = options.copy()
    filter["_model"] = ICClubDB
    filter["idclub"] = idclub
    club = await DbICClub.find_single(filter)
    club.players = [p for p in club.players if p.nature in ONPLAYERLIST]
    return club


async def anon_getICclubs() -> list[ICClubItem] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    options = {
        "_model": ICClubItem,
        "registered": True,
        "_fieldlist": {i: 1 for i in ICClubItem.model_fields.keys()},
    }
    return await DbICClub.find_multiple(options)


async def clb_getICclub(idclub: int) -> ICClubDB | None:
    """
    get IC club by idclub
    if the registration of the club exists but the club has no icclub record
    the latter is created and returned,
    returns None if nothing found
    """

    logger.info(f"clb_getICclub {idclub}")
    # we need to check if the club is registered for interclub, and if so
    registration = await find_icregistration(idclub)
    logger.info(f"got registration {registration}")
    if not registration:
        logger.info(
            f"No registration found for {idclub}, "
            "creating a non registered icclub record"
        )
        clb = await get_club_idclub(idclub)
        icc = ICClubDB(
            name=clb.name_short, idclub=idclub, players=[], registered=False, teams=[]
        )
        await create_icclub(icc)
        return await get_icclub({"idclub": idclub})
    try:
        icclub = await get_icclub({"idclub": idclub})
    except RdNotFound:
        icclub = None
    logger.info(f"got icclub {icclub}")
    if icclub and icclub.registered:
        return icclub

    # we don't have an icclub, or we didi not register the icclub
    teams = []
    ix = 1
    for t in range(registration.teams1):
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=1)
        )
        ix += 1
    for t in range(registration.teams2):
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=2)
        )
        ix += 1
    for t in range(registration.teams3):
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=3)
        )
        ix += 1
    for t in range(registration.teams4):
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=4)
        )
        ix += 1
    for t in range(registration.teams5):
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=5)
        )
        ix += 1
    if icclub:
        # we need to update the registration
        logger.info("update registration of club")
        teams_enc = [t.model_dump(exclude_unset=True) for t in teams]
        return await DbICClub.update(
            {"idclub": idclub},
            {"registered": True, "teams": teams_enc},
            {"_model": ICClubDB},
        )
    else:
        # we create the icclub
        icc = ICClubDB(
            name=registration.name,
            idclub=idclub,
            players=[],
            registered=True,
            teams=teams,
        )
        logger.info(f"create icclub {icc}")
        await create_icclub(icc)
        return await get_icclub({"idclub": idclub})


async def clb_updateICplayers(idclub: int, pi: ICPlayerUpdate) -> None:
    """
    update the the player list of a club
    """
    # TODO take care of PlayerPeriod
    icdata = await load_icdata()
    today = datetime.date.today()
    for p in icdata["playerlist_data"]:
        if p["start"] <= today <= p["end"]:
            period = p["period"]
            break
    else:
        logger.info("today not in playerlist periods")
        period = "unknown"
    icc = await clb_getICclub(idclub)
    players = pi.players
    transfersout = []
    transferdeletes = []
    inserts = []
    oldplsix = {p.idnumber: p for p in icc.players}
    newplsix = {p.idnumber: p for p in players}
    for p in newplsix.values():
        p.period = period
        idn = p.idnumber
        if idn not in oldplsix:
            # inserts
            inserts.append(p)
            if p.idclubvisit:
                if p.idcluborig == idclub:
                    transfersout.append(p)
        else:
            # check for modifications in transfer
            oldpl = oldplsix[idn]
            if oldpl.nature != p.nature:
                if p.nature in [
                    PlayerlistNature.ASSIGNED,
                    PlayerlistNature.UNASSIGNED,
                    PlayerlistNature.LOCKED,
                ]:
                    logger.info(f"player {p} moved to transferdeletes")
                    # the transfer is removed
                    transferdeletes.append(p)
                if p.nature in [
                    PlayerlistNature.EXPORTED,
                    PlayerlistNature.CONFIRMEDOUT,
                ]:
                    transfersout.append(p)
    dictplayers = [p.model_dump() for p in players]
    await DbICClub.update({"idclub": idclub}, {"players": dictplayers})
    logger.info(f"trout {transfersout} trdel {transferdeletes}")
    for t in transfersout:
        receivingclub = await clb_getICclub(t.idclubvisit)
        rcplayers = receivingclub.players
        trplayers = [x for x in rcplayers if x.idnumber == t.idnumber]
        if not trplayers:
            rcplayers.append(
                ICPlayer(
                    assignedrating=t.assignedrating,
                    fiderating=t.fiderating,
                    first_name=t.first_name,
                    idnumber=t.idnumber,
                    idcluborig=t.idcluborig,
                    idclubvisit=t.idclubvisit,
                    last_name=t.last_name,
                    natrating=t.natrating,
                    nature=PlayerlistNature.IMPORTED,
                    period=period,
                    titular=None,
                )
            )
            dictplayers = [p.model_dump() for p in rcplayers]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
    for t in transferdeletes:
        # we need to remove the transfer from the receiving club if it is existing
        try:
            receivingclub = await clb_getICclub(t.idclubvisit)
            rcplayers = receivingclub.players
            trplayers = [x for x in rcplayers if x.idnumber != t.idnumber]
            dictplayers = [p.model_dump() for p in trplayers]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
        except RdNotFound:
            pass


async def clb_validateICPlayers(
    idclub: int, pi: ICPlayerUpdate
) -> list[ICPlayerValidationError]:
    """
    creates a list of validation errors
    """

    icdata = await load_icdata()
    errors = []
    players = [p for p in pi.players if p.nature in ONPLAYERLIST]
    # check for valid elo
    elos = set()
    for p in players:
        fidenotset = False
        natnotset = False
        if not p.natrating:
            natnotset = True
            p.natrating = 0
        if not p.fiderating:
            fidenotset = True
            p.fiderating = 0
        if 1150 > p.natrating > 0:
            p.natrating = 1150
        # now we have healty values for fiderating (0 or value)
        # and natrating is minimal 1150
        maxrating = max(p.fiderating, p.natrating) + 100
        minrating = min(p.fiderating or 3000, p.natrating) - 100
        if p.assignedrating < max(icdata["notrated_elo"]["min"], minrating):
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Elo too low",
                    detail=p.idnumber,
                )
            )
        if natnotset and fidenotset:
            if p.assignedrating > icdata["notrated_elo"]["max"]:
                errors.append(
                    ICPlayerValidationError(
                        errortype="ELO",
                        idclub=idclub,
                        message="Elo too high",
                        detail=p.idnumber,
                    )
                )
        elif p.assignedrating > maxrating:
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Elo too high",
                    detail=p.idnumber,
                )
            )
        if p.assignedrating in elos:
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Double ELO",
                    detail=p.idnumber,
                )
            )
        else:
            elos.add(p.assignedrating)
    titulars = {}
    registration = await find_icregistration(idclub)
    ix = 1
    for t in range(registration.teams1):
        titulars[f"{registration.name} {ix}"] = {
            "division": 1,
            "ntitulars": icdata["ntitulars"][1],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams2):
        titulars[f"{registration.name} {ix}"] = {
            "division": 2,
            "ntitulars": icdata["ntitulars"][2],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams3):
        titulars[f"{registration.name} {ix}"] = {
            "division": 3,
            "ntitulars": icdata["ntitulars"][3],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams4):
        titulars[f"{registration.name} {ix}"] = {
            "division": 4,
            "ntitulars": icdata["ntitulars"][4],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams5):
        titulars[f"{registration.name} {ix}"] = {
            "division": 5,
            "ntitulars": icdata["ntitulars"][5],
            "counter": 0,
        }
        ix += 1
    for p in players:
        if p.titular and p.titular in titulars:
            titulars[p.titular]["counter"] += 1
    for team, tit in titulars.items():
        if tit["counter"] > tit["ntitulars"]:
            errors.append(
                ICPlayerValidationError(
                    errortype="TitularCount",
                    idclub=idclub,
                    message="Too many titulars",
                    detail=team,
                )
            )
    return errors


async def mgmt_getXlsAllplayerlist():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        ["club", "idnumber", "name", "cluborig", "rating", "F ELO", "B ELO", "Titular"]
    )
    clubs = await DbICClub.find_multiple({"_model": ICClubDB})
    for c in clubs:
        if not c.enrolled:
            continue
        sortedplayers = sorted(c.players, key=lambda x: x.assignedrating, reverse=True)
        for p in sortedplayers:
            if p.nature not in ["assigned", "requestedin"]:
                continue
            ws.append(
                [
                    c.idclub,
                    p.idnumber,
                    f"{p.last_name}, {p.first_name}",
                    p.idcluborig,
                    p.assignedrating,
                    p.fiderating,
                    p.natrating,
                    p.titular,
                ]
            )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        return Response(
            content=tmp.read(),
            headers={"Content-Disposition": "attachment; filename=allplayerlist.xlsx"},
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


async def anon_getXlsplayerlist(idclub: int):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        ["club", "idnumber", "name", "cluborig", "rating", "F ELO", "B ELO", "Titular"]
    )
    club = await DbICClub.find_single({"_model": ICClubDB, "idclub": idclub})
    sortedplayers = sorted(club.players, key=lambda x: x.assignedrating, reverse=True)
    for p in sortedplayers:
        if p.nature not in ["assigned", "requestedin"]:
            continue
        ws.append(
            [
                idclub,
                p.idnumber,
                f"{p.last_name}, {p.first_name}",
                p.idcluborig,
                p.assignedrating,
                p.fiderating,
                p.natrating,
                p.titular,
            ]
        )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        return Response(
            content=tmp.read(),
            headers={
                "Content-Disposition": f"attachment; filename=playerlist_{idclub}.xlsx"
            },
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
