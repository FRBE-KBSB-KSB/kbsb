# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# these section contains the code to read/wrtie data from the old db

from .md_interclub import (
    InterclubClub,
    InterclubClubOptional,
    InterclubClubList,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentList,
    InterclubPlayer,
    InterclubSeries,
    InterclubTransfer,
    InterclubTeam,
    InterclubVenue,
    InterclubVenuesIn,
    InterclubVenues,
    InterclubVenuesList,
    InterclubBoard,
    GameResult,
    DbInterclubClub,
    DbInterclubEnrollment,
    DbInterclubSeries,
    DbInterclubVenues,
    TransferRequestValidator,
    InterclubMatch,
    DbInterclubMatch,
)

from .interclub import (
    csv_interclubenrollments,
    csv_interclubvenues,
    find_interclubenrollment,
    find_interclubvenues_club,
    find_teamclubsseries,
    set_interclubenrollment,
    set_interclubvenues,
    add_team_to_series,
    get_announcements,
)
from .interclub_club import (
    setup_interclubclub,
    set_interclubclub,
    clear_interclubclubs,
    sortplayers_interclubclubs,
)
from .interclub_old import import_oldinterclubplayer

import kbsb.interclub.api_interclub
