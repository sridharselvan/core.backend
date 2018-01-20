# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from core.deps import bottle
app = bottle.Bottle()
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.controller.static import (
    views, javascripts, stylesheets, images
)

from core.controller.configs import (
    modify_client_config,
    view_client_config
)
from core.controller.user_interface import authenticate_user
# ----------- END: In-App Imports ---------- #


@app.route('/')
def index():
   """."""
   return views("index.html")

@app.route('/sorry_page/<page_name>', method=['GET'])
def sorry_page(page_name):
    """Serve sorry page"""
    return views("under_construction.html")


##  Web application main  ##
def main():

    # Start the Bottle webapp
    # bottle.debug(True)
    app.run(host='0.0.0.0', port=8080, reloader=True)

if __name__ == "__main__":
    main()
