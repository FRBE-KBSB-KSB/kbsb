# copyright Ruben Decrop 2012 - 2022

import logging
import telnetlib
from typing import cast, Any, Optional, List
from datetime import datetime
import io, csv

from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    encode_model,
    get_settings,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.interclub import InterclubSeries
from kbsb.club import find_club, club_locale, DbClub
from kbsb.oldkbsb import get_member
from . import DbInterclubMatch, InterclubMatch


logger = logging.getLogger(__name__)

INTERCLUB_EMAIL = "interclubs@frbe-kbsb-ksb.be"

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
#             DbInterclubMatch.p_add(
#                 InterclubMatch(
#                     division=s.division,
#                     index=s.index,
#                     round=r,
#                     home_clb=home.idclub,
#                     visit_clb=visit.idclub,
#                     boards=[],
#                 )
#             )


