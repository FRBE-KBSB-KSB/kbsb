# copyright Chessdevil Consulting BVBA 2018 - 2020

# import reddevil.boardrole.api_brole
# import reddevil.boardmember.api_bmember
import reddevil.api.api_page
import reddevil.api.api_account
import reddevil.api.api_file
import reddevil.api.api_boardrole
import reddevil.api.api_boardmember

import kbsb.api.api_member
import kbsb.api.api_club
import kbsb.api.api_book100

from .. import app

@app.get('/api')
def root():
    return {'hello': 'world'}

