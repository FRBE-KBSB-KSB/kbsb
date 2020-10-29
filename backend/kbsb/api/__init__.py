# copyright Chessdevil Consulting BVBA 2018 - 2020

import reddevil.account.api_account
import reddevil.boardrole.api_brole
import reddevil.boardmember.api_bmember
import reddevil.page.api_page
import reddevil.file.api_file

from .. import app

@app.get('/api')
def root():
    return {'hello': 'world'}

