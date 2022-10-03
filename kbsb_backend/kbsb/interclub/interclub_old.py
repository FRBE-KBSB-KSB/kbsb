# copyright Ruben Decrop 2012 - 2022

from distutils.log import debug
import logging
from typing import cast, Any, Optional, List
from datetime import datetime
import io, csv

from reddevil.core import get_settings, encode_model
from kbsb.oldkbsb import OldInterclubPlayer, ActiveMember
from kbsb.oldkbsb.old import get_member
from . import InterclubClub, InterclubClubOptional, InterclubPlayer, DbInterclubClub

logger = logging.getLogger(__name__)


async def import_oldinterclubplayer(p: OldInterclubPlayer, am_cache: dict[int, ActiveMember]):
    """
    import an oldincterclubplayer and store it in the playerlist
    uses active member cache to speed up
    """
    from .interclub_club import setup_interclubclub

    logger.info(f"procssing {p.idnumber} {p.idclub_interclub} {p.idclub_player}")
    icc = await setup_interclubclub(p.idclub_interclub)
    if not icc:
        logger.error(f"no interclubclub for {p.idclub_interclub}")
        return
    member = am_cache.get(p.idnumber, None)
    if not member: 
        logger.error(f"member  {p.idnumber} not active")
        return        
    ipl = InterclubPlayer(
        assignedrating=p.assignedrating,
        fiderating=p.fiderating or 0,
        first_name=member.first_name,
        idnumber=p.idnumber,
        idclub=p.idclub_player,
        last_name=member.last_name,
        natrating=p.natrating or 0,
    )
    players = icc.players
    ix = next((ix for ix, pl in enumerate(players) if pl.idnumber == p.idnumber), -1)
    if ix >= 0:
        players[ix] = ipl
    else:
        players.append(ipl)
    sortedplayers = sorted(players, key=lambda x: x.assignedrating, reverse=True)
    await DbInterclubClub.p_update(icc.id, InterclubClubOptional(players=sortedplayers))
    logger.debug(
        f"player {member.first_name} {member.last_name} {p.idclub_player} added to  {p.idclub_interclub}"
    )
