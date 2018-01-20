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

from core.constants import (
    STATIC_JS_FILE_PATH, STATIC_CSS_FILE_PATH, STATIC_VIEW_FILE_PATH, STATIC_IMAGE_FILE_PATH
)
# ----------- END: In-App Imports ---------- #


@app.get('/<filename:re:.*\.(tpl|html)>')
def views(filename):
    return bottle.static_file(filename, root=STATIC_VIEW_FILE_PATH)

@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename, root=STATIC_JS_FILE_PATH)

@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return bottle.static_file(filename, root=STATIC_CSS_FILE_PATH)

@app.get('/<filename:re:.*\.(jpg|jpeg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename, root=STATIC_IMAGE_FILE_PATH)
