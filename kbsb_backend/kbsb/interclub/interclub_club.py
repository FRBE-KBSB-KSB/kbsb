# copyright Ruben Decrop 2012 - 2022

import logging
from typing import cast, Any, Optional, List
from datetime import datetime

from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    get_settings,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.club import find_club, club_locale, DbClub
from kbsb.oldkbsb import get_member
from . import (
    DbInterclubClub,
    InterclubPlayer,
    InterclubTransfer,
    InterclubClub,
    InterclubClubOptional,
    TransferRequestValidator,
)
from reddevil.page.page import PageList, DbPage, isactive

logger = logging.getLogger(__name__)

from .interclub import INTERCLUB_EMAIL


async def find_interclubclub(idclub: int) -> Optional[InterclubClub]:
    """
    find a club by idclub, returns None if nothing found
    """
    logger.debug(f"find_interclubclub {idclub}")
    clubs = (await DbInterclubClub.p_find_multiple({"idclub": idclub})).clubs
    logger.debug(f"clubs {clubs}")
    return clubs[0] if clubs else None


async def setup_interclubclub(idclub: int) -> InterclubClub:
    """
    finds an interclubclub, and set it up if it does not exist
    clubs that don't partipate still get a record, but attribute teams is empty
    """
    from .interclub import find_teamclubsseries

    logger.debug(f"setup_interclubclub {idclub}")
    icc = await find_interclubclub(idclub)
    if icc:
        return icc
    logger.debug(f"no icc for {idclub}")
    teams = await find_teamclubsseries(idclub)
    if teams:
        name = " ".join(teams[0].name.split()[:-1])
        icc = InterclubClub(
            name=name,
            idclub=idclub,
            teams=teams,
            players=[],
            transfersout=[],
        )
    else:
        name = (await find_club(idclub)).name_short
        icc = InterclubClub(
            name=name,
            idclub=idclub,
            teams=[],
            players=[],
            transfersout=[],
        )
    logger.info(f"creating icc for club {idclub}")
    id = await DbInterclubClub.add(
        {
            "name": icc.name,
            "idclub": icc.idclub,
            "teams": [t.dict() for t in icc.teams],
            "players": [],
            "transfersout": [],
        }
    )
    logger.info(f"icc id {id}")
    # return await DbInterclubClub.p_find_single({"id", id})


async def transfer_players(requester: int, tr: TransferRequestValidator) -> None:
    """
    perform a transfer of a list of players
    """
    origclub = await find_interclubclub(tr.idoriginalclub)
    if not origclub:
        raise RdNotFound(description="InterclubOrigClubNotFound")
    visitclub = await find_interclubclub(tr.idvisitingclub)
    if not visitclub:
        raise RdNotFound(description="InterclubVisitClubNotFound")
    if not visitclub.teams:
        raise RdBadRequest(description="VisitingClubNotParticipating")
    for m in tr.members:
        am = get_member(m)
        if not am:
            logger.info("cannot transfer player {m} because player is inactive")
            continue
        ict = InterclubTransfer(
            idnumber=m,
            idoriginalclub=tr.idoriginalclub,
            idvisitingclub=tr.idvisitingclub,
            request_date=datetime.utcnow(),
            request_id=requester,
        )
        # check if member is in orig playerlist and remove if necessary
        for ix, p in enumerate(origclub.players):
            if p.idnumber == m:
                origclub.players.pop(ix)
                break
        # check if member is in orig transfersout and remove if necessary
        for ix, p in enumerate(origclub.transfersout):
            if p.idnumber == m:
                origclub.transfersout.pop(ix)
                break
        # fill in the transfer in origclub.transfersout
        origclub.transfersout.append(ict)
        # add player to visitclub.playerlist
        for ix, p in enumerate(visitclub.players):
            if p.idnumber == m:
                break
        else:
            visitclub.players.append(
                InterclubPlayer(
                    assignedrating=max(am.fiderating, am.natrating),
                    fiderating=am.fiderating,
                    first_name=am.first_name,
                    idnumber=m,
                    idclub=origclub.idclub,
                    natrating=am.natrating,
                    last_name=am.last_name,
                    transfer=True,
                )
            )
    DbInterclubClub.p_update(
        origclub.id,
        InterclubClubOptional(
            players=origclub.players, transfersout=origclub.transfersout
        ),
    )
    DbInterclubClub.p_update(
        visitclub.id, InterclubClubOptional(players=visitclub.players)
    )


async def update_clublist(idclub: int, playerlist: List[int]) -> None:
    """
    update the clublist with a list of members, belonging to that club
    """
    icc = await find_interclubclub(idclub)
    playerset = {p.idnumber for p in icc.players}
    for p in playerlist:
        am = get_member(p)
        if not am:
            logger.info("cannot add player {m} to clublist: player is inactive")
            continue
        if am.idclub != idclub:
            logger.info(
                "cannot add player {m} to clublist player is not member of {idclub}"
            )
            continue
        if p in playerset:
            continue
        playerset.add(p)
        icc.players.append(
            InterclubPlayer(
                assignedrating=max(am.fiderating, am.natrating),
                fiderating=am.fiderating,
                first_name=am.first_name,
                idnumber=p,
                idclub=icc.idclub,
                natrating=am.natrating,
                last_name=am.last_name,
                transfer=False,
            )
        )
    DbInterclubClub.p_update(icc.id, InterclubClubOptional(players=icc.players))


async def set_interclubclub(idclub: int, icc: InterclubClubOptional) -> InterclubClub:
    """
    updates the interclubclub
    """
    club = await find_club(idclub)
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    ic = await find_interclubclub(idclub)
    settings = get_settings()
    icupdated = await DbInterclubClub.p_update(ic.id, icc)
    receiver = (
        [club.email_main, INTERCLUB_EMAIL] if club.email_main else [INTERCLUB_EMAIL]
    )
    if club.email_interclub:
        receiver.append(club.email_interclub)
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["blindcopy"],
        subject="Interclub 2022-23",
        template="interclub/club_{locale}.md",
    )
    icdict = icupdated.dict()
    icdict["locale"] = locale
    sendEmail(mp, icdict, "interclub playerlist")
    return icupdated


# games

rounds = {
    1: ((1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)),
    2: ((12, 7), (8, 6), (9, 5), (10, 4), (11, 3), (1, 2)),
    3: ((2, 12), (3, 1), (4, 11), (5, 10), (6, 9), (2, 9)),
    4: ((12, 8), (9, 7), (10, 6), (11, 5), (1, 4), (2, 3)),
    5: ((3, 12), (4, 2), (5, 1), (6, 11), (7, 10), (8, 9)),
    6: ((12, 9), (10, 8), (11, 7), (1, 6), (2, 5), (3, 4)),
    7: ((4, 12), (5, 3), (6, 2), (7, 1), (8, 11), (9, 10)),
    8: ((12, 10), (11, 9), (1, 8), (2, 7), (3, 6), (4, 5)),
    9: ((5, 12), (6, 4), (7, 3), (8, 2), (9, 1), (10, 11)),
    10: ((12, 11), (1, 10), (2, 9), (3, 8), (4, 7), (5, 6)),
    11: ((6, 12), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1)),
}


# async def create_interclub_games(s: InterclubSeries):
#     """
#     create interclub games for a serie
#     """
#     for r, matches in round.items():
#         for m in matches:
#             home = next(t for t in s.teams if t["pairingnumber"] == m[0])
#             visit = next(t for t in s.teams if t["pairingnumber"] == m[1])
#             DbInterclubGame.p_add(
#                 InterclubGame(
#                     division=s.division,
#                     index=s.index,
#                     round=r,
#                     home_clb=home.idclub,
#                     visit_clb=visit.idclub,
#                     boards=[],
#                 )
#             )


async def get_announcements() -> PageList:
    """
    get all the pages
    """
    dl = await DbPage.find_multiple(
        {
            "doctype": "interclub",
            "enabled": True,
            "_fieldlist": [
                "creationtime",
                "enabled",
                "expirationdate",
                "name",
                "modificationtime",
                "publicationdate",
                "slug",
                "id",
                "body",
                "intro",
                "title",
            ],
            "publicationdate": {"$ne": ""},
        }
    )
    ap = [x for x in dl if isactive(x)]
    ap = sorted(ap, key=lambda x: x["publicationdate"], reverse=True)
    return PageList(items=ap)
