# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# these section contains the code to read/wrtie data from the old db

from .md_interclub import (
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentUpdate,
    InterclubPlayer,
    InterclubPrevious,
    InterclubSerie,
    InterclubTeam,
    InterclubEnrollmentList,
    InterclubVenue,
    InterclubVenueList,
    InterclubVenues,
    InterclubVenuesList,
)

from .db_interclub import (
    DbInterclubEnrollment,
    DbInterclubVenues,
    DbInterclubPrevious,
)

from .interclub import (
    find_interclubenrollment,
    find_interclubvenues_club,
    make_interclubenrollment,
    modify_interclubenrollment,
    set_interclubvenues,
)

import kbsb.interclub.api_interclub
