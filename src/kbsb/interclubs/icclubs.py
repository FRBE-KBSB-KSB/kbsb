# copyright Ruben Decrop 2012 - 2024

import logging
from tempfile import NamedTemporaryFile
from typing import Any, cast

import openpyxl
from reddevil.core import (
    RdNotFound,
    get_settings,
)

from kbsb.club import get_club_idclub
from kbsb.interclubs import (
    DbICClub,
    DbICClub2324,
    DbICClub2425,
    DbICClub2526,
    DbICSeries,
    ICClubDB,
    ICClubItem,
    ICPlayer,
    ICPlayerUpdate,
    ICPlayerValidationError,
    ICTeam,
    PlayerlistNature,
    PlayerPeriod,
    load_icdata,
)
from kbsb.interclubs.registrations import find_icregistration

logger = logging.getLogger(__name__)

settings = get_settings()

# Interclub Clubs, Playerlist and Teams

ONPLAYERLIST = [
    PlayerlistNature.ASSIGNED,
    PlayerlistNature.IMPORTED,
    PlayerlistNature.REQUESTEDIN,
]

# archive
dbclubs = {
    "2324": DbICClub2324,
    "2425": DbICClub2425,
    "2526": DbICClub2526,
}

# CRUD


async def create_icclub(icclub: ICClubDB) -> str:
    """
    create a new InterclubClub returning its id
    """
    icclubdict = icclub.model_dump()
    icclubdict.pop("id", None)
    return await DbICClub.add(icclubdict)  # pyright: ignore[reportReturnType]


async def get_icclub(options: dict | None = None) -> ICClubDB | None:
    """
    get IC club by idclub, returns None if nothing found
    filter players for active players
    """
    filter = options.copy() if options else {}
    filter["_model"] = filter.get("_model", ICClubDB)
    logger.info(f"get icclub {filter}")
    club = await DbICClub.find_single(filter)
    return club


async def update_icclub(
    iu: ICClubDB, options: dict[str, Any] | None = None
) -> ICClubDB:
    """
    update a interclub club
    """
    logger.info(f"update icclub {iu.idclub}")
    options1 = options.copy() if options else {}
    options1["_model"] = options1.pop("_model", ICClubDB)
    iudict = iu.model_dump(exclude_unset=True)
    return cast(
        ICClubDB,
        await DbICClub.update({"idclub": iu.idclub}, iudict, options1),
    )


# Business methods


async def anon_getICteams(idclub: int, options: dict = {}) -> list[ICTeam]:
    """
    get all the interclub teams for a club available in all divisions
    """
    series = await DbICSeries.find_multiple({"teams.idclub": idclub})
    teams = []
    for s in series:
        for t in s.teams:  # pyright: ignore[reportAttributeAccessIssue]
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
    club.players = [p for p in club.players if p.nature in ONPLAYERLIST]  # pyright: ignore[reportAttributeAccessIssue]
    return club  # pyright: ignore[reportReturnType]


async def anon_getICclub_archive(
    season: str, idclub: int, options: dict[str, Any] | None = None
) -> ICClubDB | None:
    """
    get IC club by idclub, returns None if nothing found
    filter players for active players
    """
    dbclub = dbclubs[season]
    filter = options.copy() if options else {}
    filter["_model"] = ICClubDB
    filter["idclub"] = idclub
    club = await dbclub.find_single(filter)
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
    return await DbICClub.find_multiple(options)  # pyright: ignore[reportReturnType]


async def mgmt_getICclubs() -> list[ICClubDB]:
    """
    get IC club by idclub, returns None if nothing found
    """
    options = {"_model": ICClubDB}
    return await DbICClub.find_multiple(options)  # pyright: ignore[reportReturnType]


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
            name=clb.name_short,
            idclub=idclub,
            players=[],
            registered=False,
            teams=[],  # pyright: ignore[reportOptionalMemberAccess]
        )
        await create_icclub(icc)
        return await get_icclub({"idclub": idclub})
    try:
        icclub = await get_icclub({"idclub": idclub})
    except RdNotFound:
        icclub = None
    if icclub and icclub.registered:
        return icclub

    # we don't have an icclub, or we didi not register the icclub
    teams = []
    ix = 1
    for t in range(registration.teams1):  # pyright: ignore[reportArgumentType]
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=1)
        )
        ix += 1
    for t in range(registration.teams2):  # pyright: ignore[reportArgumentType]
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=2)
        )
        ix += 1
    for t in range(registration.teams3):  # pyright: ignore[reportArgumentType]
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=3)
        )
        ix += 1
    for t in range(registration.teams4):  # pyright: ignore[reportArgumentType]
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=4)
        )
        ix += 1
    for t in range(registration.teams5):  # pyright: ignore[reportArgumentType]
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=5)
        )
        ix += 1
    for t in range(registration.teams6):  # pyright: ignore[reportArgumentType]
        teams.append(
            ICTeam(idclub=idclub, name=f"{registration.name} {ix}", division=6)
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
        )  # pyright: ignore[reportReturnType]
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
    logger.info(f"clb_updateICplayers {idclub}")
    icc = await clb_getICclub(idclub)
    players = pi.players
    transfersout = []
    transferdeletes = []
    oldplsix = {p.idnumber: p for p in icc.players}  # pyright: ignore[reportOptionalMemberAccess]
    newplsix = {p.idnumber: p for p in players}
    for p in newplsix.values():
        idn = p.idnumber
        if idn not in oldplsix:
            # player contains an insert
            if p.idclubvisit and p.idcluborig == idclub:
                transfersout.append(p)
        else:
            # player already exists, check for modifications in transfer
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
        rcplayers = receivingclub.players  # pyright: ignore[reportOptionalMemberAccess]
        trplayers = [x for x in rcplayers if x.idnumber == t.idnumber]  # pyright: ignore[reportOptionalIterable]
        if not trplayers:
            rcplayers.append(  # pyright: ignore[reportOptionalMemberAccess]
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
                    period=t.period,
                    titular=None,
                )
            )
            dictplayers = [p.model_dump() for p in rcplayers]  # pyright: ignore[reportOptionalIterable]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
    for t in transferdeletes:
        # we need to remove the transfer from the receiving club if it is existing
        try:
            receivingclub = await clb_getICclub(t.idclubvisit)
            rcplayers = receivingclub.players  # pyright: ignore[reportOptionalMemberAccess]
            trplayers = [x for x in rcplayers if x.idnumber != t.idnumber]  # pyright: ignore[reportOptionalIterable]
            dictplayers = [p.model_dump() for p in trplayers]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
        except Exception as e:
            logger.error(f"Error updating receiving club: {e}")


async def mgmt_updateICplayers(idclub: int, pi: ICPlayerUpdate) -> None:
    """
    update the the player list of a club
    """
    logger.info(f"clb_updateICplayers {idclub}")
    icc = await clb_getICclub(idclub)
    players = pi.players
    transfersout = []
    transferdeletes = []
    oldplsix = {p.idnumber: p for p in icc.players}  # pyright: ignore[reportOptionalMemberAccess, reportOptionalIterable]
    newplsix = {p.idnumber: p for p in players}
    period = PlayerPeriod.SEPTEMBER
    for p in newplsix.values():
        idn = p.idnumber
        if idn not in oldplsix:
            # inserts
            if p.idclubvisit and p.idcluborig == idclub:
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
        rcplayers = receivingclub.players  # pyright: ignore[reportOptionalMemberAccess]
        trplayers = [x for x in rcplayers if x.idnumber == t.idnumber]  # pyright: ignore[reportOptionalIterable]
        if not trplayers:
            rcplayers.append(  # pyright: ignore[reportOptionalMemberAccess]
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
                    period=t.period,
                    titular=None,
                )
            )
            dictplayers = [p.model_dump() for p in rcplayers]  # pyright: ignore[reportOptionalIterable]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
    for t in transferdeletes:
        # we need to remove the transfer from the receiving club if it is existing
        try:
            receivingclub = await clb_getICclub(t.idclubvisit)
            rcplayers = receivingclub.players  # pyright: ignore[reportOptionalMemberAccess]
            trplayers = [x for x in rcplayers if x.idnumber != t.idnumber]  # pyright: ignore[reportOptionalIterable]
            dictplayers = [p.model_dump() for p in trplayers]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
        except Exception as e:
            logger.error(f"Error updating receiving club: {e}")


async def clb_validateICPlayers(
    idclub: int, pi: ICPlayerUpdate
) -> list[ICPlayerValidationError]:
    """
    creates a list of validation errors
    """

    icdata = await load_icdata()
    assert icdata
    errors = []
    players = [p for p in pi.players if p.nature in ONPLAYERLIST]
    # check for valid elo
    elos = set()
    for p in players:
        if not p.fiderating:
            p.fiderating = 0
        maxrating = (
            p.fiderating + 100 if p.fiderating else icdata["notrated_elo"]["max"]
        )
        minrating = (
            p.fiderating - 100 if p.fiderating else icdata["notrated_elo"]["min"]
        )
        if p.assignedrating < minrating:
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Elo too low",
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
    # check for titulars
    titulars = {}
    registration = await find_icregistration(idclub)
    assert registration
    ix = 1
    for t in range(registration.teams1):  # pyright: ignore[reportArgumentType]
        titulars[f"{registration.name} {ix}"] = {
            "division": 1,
            "ntitulars": icdata["ntitulars"][1],
            "maxtitulars": icdata["maxtitulars"][1],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams2):  # pyright: ignore[reportArgumentType]
        titulars[f"{registration.name} {ix}"] = {
            "division": 2,
            "ntitulars": icdata["ntitulars"][2],
            "maxtitulars": icdata["maxtitulars"][2],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams3):  # pyright: ignore[reportArgumentType]
        titulars[f"{registration.name} {ix}"] = {
            "division": 3,
            "ntitulars": icdata["ntitulars"][3],
            "maxtitulars": icdata["maxtitulars"][3],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams4):  # pyright: ignore[reportArgumentType]
        titulars[f"{registration.name} {ix}"] = {
            "division": 4,
            "ntitulars": icdata["ntitulars"][4],
            "maxtitulars": icdata["maxtitulars"][4],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams5):  # pyright: ignore[reportArgumentType]
        titulars[f"{registration.name} {ix}"] = {
            "division": 5,
            "ntitulars": icdata["ntitulars"][5],
            "maxtitulars": icdata["maxtitulars"][5],
            "counter": 0,
        }
        ix += 1
    for t in range(registration.teams6):  # pyright: ignore[reportArgumentType]
        titulars[f"{registration.name} {ix}"] = {
            "division": 6,
            "ntitulars": icdata["ntitulars"][6],
            "maxtitulars": icdata["maxtitulars"][6],
            "counter": 0,
        }
        ix += 1
    for p in players:
        if p.titular and p.titular in titulars:
            titulars[p.titular]["counter"] += 1
    for team, tit in titulars.items():
        if tit["counter"] > tit["maxtitulars"]:
            errors.append(
                ICPlayerValidationError(
                    errortype="TitularCount",
                    idclub=idclub,
                    message="Too many titulars",
                    detail=team,
                )
            )
        if tit["counter"] < tit["ntitulars"]:
            errors.append(
                ICPlayerValidationError(
                    errortype="TitularCount",
                    idclub=idclub,
                    message="Not enough titulars",
                    detail=team,
                )
            )
    return errors


async def mgmt_get_xlsplayerlists():
    """
    get excel file for combined playerlists of all clubs
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(  # pyright: ignore[reportOptionalMemberAccess]
        ["club", "idnumber", "name", "cluborig", "rating", "F ELO", "B ELO", "Titular"]
    )
    clubs = await DbICClub.find_multiple({"_model": ICClubDB})
    for c in clubs:
        if not c.registered:  # pyright: ignore[reportAttributeAccessIssue]
            continue
        sortedplayers = sorted(c.players, key=lambda x: x.assignedrating, reverse=True)  # pyright: ignore[reportAttributeAccessIssue]
        for p in sortedplayers:
            if p.nature not in ["assigned", "imported"]:
                continue
            ws.append(  # pyright: ignore[reportOptionalMemberAccess]
                [
                    c.idclub,  # pyright: ignore[reportAttributeAccessIssue]
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
        xlscontent = tmp.read()
    return xlscontent


async def anon_get_xlsplayerlist(idclub: int):
    """
    get excel file of playerlist of a club
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(  # pyright: ignore[reportOptionalMemberAccess]
        ["club", "idnumber", "name", "cluborig", "rating", "F ELO", "B ELO", "Titular"]
    )
    club = await DbICClub.find_single({"_model": ICClubDB, "idclub": idclub})
    sortedplayers = sorted(club.players, key=lambda x: x.assignedrating, reverse=True)  # pyright: ignore[reportAttributeAccessIssue]
    for p in sortedplayers:
        if p.nature not in ["assigned", "imported"]:
            continue
        ws.append(  # pyright: ignore[reportOptionalMemberAccess]
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
        xlscontent = tmp.read()
    return xlscontent
