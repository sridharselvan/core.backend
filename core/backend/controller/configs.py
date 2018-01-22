# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from bottle import request as brequest
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.backend.utils.butils import decode_form_data
from core.backend.controller import app, bottle
from core.backend.utils.core_utils import common_route
from core.backend.config import (
    generate_client_config, update_client_config, view_client_config
)

# ----------- END: In-App Imports ---------- #

@app.get('/viewclientconfig')
@common_route
def show_client_config():
    return view_client_config()


@app.get('/modifyclientconfig', method='POST')
@common_route
def modify_client_config():
    form_data = decode_form_data(brequest.forms)
    return update_client_config(form_data)
