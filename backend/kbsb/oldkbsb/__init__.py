# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# these section contains the code to interact with the old mysqldb

from .md_old import (
    OldClub_sql,
    OldLoginValidator,
    OldMember,
    OldMember_sql,
    OldMemberList,
    OldUser,
    OldUser_sql,
    old_role_mapping,
    OldNatRating_sql,
    OldNatRating,
    OldFideRating_sql,
    OldFideRating,
    ActiveMember,
    ActiveMemberList,
    OldInterclubPlayer,
    OldInterclubGames,
    OldInterclubGamesList,
)

from .old import (
    old_login,
    validate_oldtoken,
    get_activemembers,
    get_member,
    get_clubmembers,
    get_member,
    get_oldinterclubplayers,
    get_oldinterclubgames,
)

import kbsb.oldkbsb.api_old
