# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2020

import reddevil.account.api_account
import reddevil.boardrole.api_brole
import reddevil.boardmember.api_bmember
import reddevil.page.api_page

from .. import app

@app.get('/api')
def root():
    return {'hello': 'world'}


