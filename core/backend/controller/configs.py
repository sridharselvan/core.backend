# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from core.deps.bottle import request as brequest
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.butils import decode_form_data
from core.controller import app, bottle

from core.config import (
    generate_client_config, update_client_config, view_client_config
)

# ----------- END: In-App Imports ---------- #

@app.get('/viewclientconfig')
def modify_client_config():
    return view_client_config()


@app.get('/modifyclientconfig', method='POST')
def modify_client_config():
    form_data = decode_form_data(brequest.forms)
    return update_client_config(form_data)
