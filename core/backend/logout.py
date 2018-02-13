# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import json
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from sqlalchemy.exc import SQLAlchemyError
# ----------- END: Third Party Imports ---------- #
from bottle import request
# ----------- START: In-App Imports ---------- #
from core.db.model import (
    UserSessionModel, CodeStatusModel
)

from core.backend.utils.butils import decode_form_data

from core.backend.utils.core_utils import use_transaction
# ----------- END: In-App Imports ---------- #

def logout_session(session, *args, **kwargs):

    code_status_data = CodeStatusModel.fetch_status_idn(session, status='loggedout')
    user_session = request.environ.get('beaker.session')
    user_id = user_session['user_id']

    UserSessionModel.update_active_user_session(
        session, user_idn=user_id, status_idn=code_status_data
    )


