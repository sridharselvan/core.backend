# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.controller import app, bottle

from core.api.user import authenticate_user, create_user
# ----------- END: In-App Imports ---------- #
 
@app.get('/loginvalidation', method='POST')
def on_login():
    return authenticate_user()

@app.get('/createUser', method='POST')
def on_create_user():
    return create_user()

